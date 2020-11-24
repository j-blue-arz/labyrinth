""" This module contains methods to build and initialize games, boards and mazes.

There are two ways of creating these objects: either by fully specifying all details, or
by randomly generating layouts based with certain restrictions, based on the original game. """
import random
import math
from labyrinth.model.game import MazeCard, Maze, BoardLocation, Board, Game, Turns
from labyrinth.model.exceptions import InvalidSizeException


class MazeCardFactory:
    """ Constructs maze cards, taking care of unique ids """
    def __init__(self):
        self._next_id = 0

    def reset_ids(self):
        """ Resets the instance counter, such that a newly generated instance will have ID of 0 """
        self._next_id = 0

    def create_instance(self, out_paths, rotation):
        """Generates a new instance, with autoincreasing ID.
        """
        maze_card = MazeCard(self._next_id, out_paths, rotation)
        self._next_id = self._next_id + 1
        return maze_card

    def create_random_maze_card(self, out_paths=None):
        """ Creates a new instance of MazeCard with
        random out_paths and rotation
        """
        if not out_paths:
            out_paths = random.choice([MazeCard.STRAIGHT, MazeCard.CORNER, MazeCard.T_JUNCT])
        rotation = random.choice([0, 90, 180, 270])
        return self.create_instance(out_paths, rotation)


def create_maze_and_leftover(size=7):
    """ Generates a random maze state with a given odd size.
    The layout rules of the original game are obeyed, with a few generalizations for sizes > 7.
    Corners of the maze are fixed as corners.
    All other fixed maze cards are t-junctions. If there is a fixed middle maze card (for size = 4k + 1), it is a cross.
    The trunk of a fixed t-junction points to the center,
    e.g. the t-junction at position (0, 2) is rotated by 90 degrees (pointing S).
    If the t-junction is placed on the diagonal, it behaves as if it were placed in
    a counter-clockwise position: (2, 2) points to W.
    For a size of 7 (original game), there are 16 fixed cards. 15 corners, 6 t-junctions, and 13 straights are then
    randomly placed on the board, with the last remaing card beeing returned as the leftover.
    The ratios are approximately kept for other sizes, rounding in favor of corners and then straights.
    """
    if _even(size) or not 2 < size < 32:
        raise InvalidSizeException("Requested size {} is not an odd number between 2 and 32.".format(size))
    maze = Maze(maze_size=size)

    fixed_cards = _determine_fixed_cards(size)
    remaining = size*size+1 - len(fixed_cards)
    free_cards_out_paths = _determine_free_cards_out_paths(remaining)
    card_factory = MazeCardFactory()
    free_cards = [card_factory.create_random_maze_card(out_paths=out_paths) for out_paths in free_cards_out_paths]
    random.shuffle(free_cards)
    card_iter = iter(free_cards)

    for location in maze.maze_locations:
        if location in fixed_cards:
            maze[location] = card_factory.create_instance(fixed_cards[location].out_paths,
                                                          fixed_cards[location].rotation)
        else:
            maze[location] = card_iter.__next__()

    leftover = card_iter.__next__()
    return maze, leftover


def _determine_fixed_cards(size):
    """ Determines the locations, out paths and rotations for the fixed cards,
    according to the layout of the original game. The layout is generalized to arbitrary
    sizes.
    Returns a map from location to MazeCard. """
    maze = Maze(maze_size=size)
    border = size - 1
    center = border // 2
    fixed_corners = {
        BoardLocation(0, 0): MazeCard(out_paths=MazeCard.CORNER, rotation=90),
        BoardLocation(0, border): MazeCard(out_paths=MazeCard.CORNER, rotation=180),
        BoardLocation(border, border): MazeCard(out_paths=MazeCard.CORNER, rotation=270),
        BoardLocation(border, 0): MazeCard(out_paths=MazeCard.CORNER, rotation=0)}
    fixed_center = {}
    if border % 4 == 0:
        fixed_center[BoardLocation(center, center)] = MazeCard(out_paths=MazeCard.CROSS)
    fixed_locations = [location for location in maze.maze_locations if _even(location.column) and _even(location.row)]
    fixed_t_juncts_locations = [location for location in fixed_locations
                                if location not in fixed_corners and location not in fixed_center]

    fixed_t_juncts = {location: MazeCard(out_paths=MazeCard.T_JUNCT,
                                         rotation=_rotation_of_fixed_t_junct(location, size))
                      for location in fixed_t_juncts_locations}
    fixed_cards = {**fixed_corners, **fixed_t_juncts, **fixed_center}
    return fixed_cards


def _determine_free_cards_out_paths(remaining):
    """ Determines the out paths of the free cards, according to the distribution of maze cards
    in the original game. This distribution is generalized to arbitrary sizes.
    Returns a list of out paths. """
    num_corners = math.floor(remaining * 15 / 34)
    num_t_juncts = math.floor(remaining * 6 / 34)
    num_straights = math.floor(remaining * 13 / 34)
    remaining = remaining - num_corners - num_t_juncts - num_straights
    if remaining > 0:
        num_corners += 1
    if remaining > 1:
        num_straights += 1

    free_cards_out_paths = [MazeCard.CORNER]*num_corners + \
                           [MazeCard.T_JUNCT]*num_t_juncts +  \
                           [MazeCard.STRAIGHT]*num_straights
    return free_cards_out_paths


def _rotation_of_fixed_t_junct(location, size):
    border = size - 1
    col = location.column
    row = location.row
    if col <= row < border-col:
        return 0
    if row < col <= border-row:
        return 90
    if border-col < row <= col:
        return 180
    return 270


def _even(number):
    return number % 2 == 0


def create_board(maze_size=7):
    """ Creates a board with a given maze size.

    The maze and the leftover obey the generalized original-game layout and maze card distribution rules """
    maze, leftover = create_maze_and_leftover(size=maze_size)
    return Board(maze=maze, leftover_card=leftover)


def create_game(maze_size=7, game_id=0, with_delay=True):
    """ Creates a game instance with a random board. Player and piece initialization
    is not done here. """
    if not with_delay:
        return Game(game_id, board=create_board(maze_size), turns=Turns())
    else:
        return Game(game_id, board=create_board(maze_size))


def create_maze(maze_string, maze_card_factory=None):
    """ Reads a multi-line string representing a labyrinth configuration.
    Each maze card is a 3*3 substring of this multiline string. Walls are represented by '#',
    paths with '.'. After each field, there is one delimiter symbol, both horizontally and vertically.
    First line starts at index 1. """
    if not maze_card_factory:
        maze_card_factory = MazeCardFactory()

    maze = Maze()

    lines = maze_string.splitlines()[1:]
    maze_size = len(lines[0]) // 4
    maze = Maze(maze_size=maze_size)

    def field(row, col):
        row_lines = lines[row*4:row*4 + 3]
        field_lines = [row_line[col*4:col*4+3] for row_line in row_lines]
        return field_lines

    def create_maze_card(field):
        line_to_maze_card = {
            "###...###": (MazeCard.STRAIGHT, 90),
            "#.##.##.#": (MazeCard.STRAIGHT, 0),
            "#.##..###": (MazeCard.CORNER, 0),
            "####..#.#": (MazeCard.CORNER, 90),
            "###..##.#": (MazeCard.CORNER, 180),
            "#.#..####": (MazeCard.CORNER, 270),
            "#.##..#.#": (MazeCard.T_JUNCT, 0),
            "###...#.#": (MazeCard.T_JUNCT, 90),
            "#.#..##.#": (MazeCard.T_JUNCT, 180),
            "#.#...###": (MazeCard.T_JUNCT, 270),
            "#.#...#.#": (MazeCard.CROSS, 0)
        }
        line = "".join(field)
        try:
            maze_card_parameters = line_to_maze_card[line]
            return maze_card_factory.create_instance(*maze_card_parameters)
        except KeyError:
            return None

    for location in maze.maze_locations:
        maze[location] = create_maze_card(field(location.row, location.column))

    return maze
