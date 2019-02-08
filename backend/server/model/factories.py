""" This module contains methods to build and initialize games, boards and mazes.

There are two ways of creating these objects: either by fully specifying all details, or
by randomly generating layouts based with certain restrictions, based on the original game. """
import random
import math
from server.model.game import MazeCard, Maze, BoardLocation, Board, Game
from server.model.exceptions import InvalidSizeException

def even(number):
    return number % 2 == 0

def create_random_maze_card(doors=None):
    """ Creates a new instance of MazeCard with
    random doors and rotation
    """
    if not doors:
        doors = random.choice([MazeCard.STRAIGHT, MazeCard.CORNER, MazeCard.T_JUNCT])
    rotation = random.choice([0, 90, 180, 270])
    return MazeCard.create_instance(doors, rotation)


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
    if even(size) or not 2 < size < 32:
        raise InvalidSizeException("Requested size {} is not an odd number between 2 and 32.".format(size))
    maze = Maze(maze_size=size)

    border = size - 1
    center = border // 2
    fixed_corners = {
        BoardLocation(0, 0): MazeCard(doors=MazeCard.CORNER, rotation=90),
        BoardLocation(0, border): MazeCard(doors=MazeCard.CORNER, rotation=180),
        BoardLocation(border, border): MazeCard(doors=MazeCard.CORNER, rotation=270),
        BoardLocation(border, 0): MazeCard(doors=MazeCard.CORNER, rotation=0)}
    fixed_center = {}
    if border % 4 == 0:
        fixed_center[BoardLocation(center, center)] = MazeCard(doors=MazeCard.CROSS)
    fixed_locations = [location for location in maze.maze_locations if even(location.column) and even(location.row)]
    fixed_t_juncts_locations = [location for location in fixed_locations
                                if location not in fixed_corners and location not in fixed_center]

    def rotation(location):
        col = location.column
        row = location.row
        if col <= row < border-col:
            return 0
        if row < col <= border-row:
            return 90
        if border-col < row <= col:
            return 180
        return 270

    fixed_t_juncts = {location: MazeCard(doors=MazeCard.T_JUNCT, rotation=rotation(location))
                      for location in fixed_t_juncts_locations}
    fixed_cards = {**fixed_corners, **fixed_t_juncts, **fixed_center}

    remaining = size*size+1 - len(fixed_cards)
    num_corners = math.floor(remaining * 15 / 34)
    num_t_juncts = math.floor(remaining * 6 / 34)
    num_straights = math.floor(remaining * 13 / 34)
    remaining = remaining - num_corners - num_t_juncts - num_straights
    if remaining > 0:
        num_corners += 1
    if remaining > 1:
        num_straights += 1

    loose_cards_doors = [MazeCard.CORNER]*num_corners + \
                        [MazeCard.T_JUNCT]*num_t_juncts +  \
                        [MazeCard.STRAIGHT]*num_straights
    MazeCard.reset_ids()
    loose_cards = [create_random_maze_card(doors=doors) for doors in loose_cards_doors]
    random.shuffle(loose_cards)
    card_iter = iter(loose_cards)

    for location in maze.maze_locations:
        if location in fixed_cards:
            maze[location] = MazeCard.create_instance(fixed_cards[location].doors, fixed_cards[location].rotation)
        else:
            maze[location] = card_iter.__next__()

    leftover = card_iter.__next__()
    return maze, leftover


def create_fixed_board(maze_string, leftover_doors=None, start_locations=None, objective_location=None):
    """ Creates a Board instance. Random maze, random leftover. """
    maze = create_maze(maze_string)
    if start_locations:
        Board.START_LOCATIONS = start_locations
    if objective_location:
        Board.OBJECTIVE_LOCATION = objective_location
    return Board(maze=maze, leftover_card=create_random_maze_card(leftover_doors))


def create_fixed_game(maze_string, game_id=0, leftover_doors=None,
                      start_coordinates=None, objective_coordinates=None):
    """ Creates a game with a well-defined board state. Maze, leftover,
    starting coordinates of pieces and objective location can be specified
    """
    start_locations, objective_location = None, None
    if start_coordinates:
        start_locations = [BoardLocation(*coordinates) for coordinates in start_coordinates]
    if objective_coordinates:
        objective_location = BoardLocation(*objective_coordinates)
    return Game(game_id, board=create_fixed_board(maze_string, leftover_doors, start_locations, objective_location))


def create_board(maze_size=7):
    """ Creates a board with a given maze size """
    maze, leftover = create_maze_and_leftover(size=maze_size)
    return Board(maze=maze, leftover_card=leftover)

def create_game(maze_size=7, game_id=0):
    """ Creates a game instance with a random board. Player and piece initialization
    is not done here. """
    return Game(game_id, board=create_board(maze_size))


def create_maze(maze_string):
    """ Reads a multi-line string representing a labyrinth configuration.
    Each maze card is a 3*3 substring of this multiline string. Walls are represented by '#',
    paths with '.'. After each field, there is one delimiter symbol, both horizontally and vertically.
    First line starts at index 1. """
    maze = Maze()

    lines = maze_string.splitlines()[1:]
    maze_size = len(lines[0]) // 4
    maze = Maze(maze_size=maze_size)

    def field(row, col):
        row_lines = lines[row*4:row*4 + 3]
        field_lines = [row_line[col*4:col*4+3] for row_line in row_lines]
        return field_lines

    def create_maze_card(field):
        line = "".join(field)
        if line == "###...###":
            return MazeCard.create_instance(doors=MazeCard.STRAIGHT, rotation=90)
        if line == "#.##.##.#":
            return MazeCard.create_instance(doors=MazeCard.STRAIGHT, rotation=0)
        if line == "#.##..###":
            return MazeCard.create_instance(doors=MazeCard.CORNER, rotation=0)
        if line == "####..#.#":
            return MazeCard.create_instance(doors=MazeCard.CORNER, rotation=90)
        if line == "###..##.#":
            return MazeCard.create_instance(doors=MazeCard.CORNER, rotation=180)
        if line == "#.#..####":
            return MazeCard.create_instance(doors=MazeCard.CORNER, rotation=270)
        if line == "#.##..#.#":
            return MazeCard.create_instance(doors=MazeCard.T_JUNCT, rotation=0)
        if line == "###...#.#":
            return MazeCard.create_instance(doors=MazeCard.T_JUNCT, rotation=90)
        if line == "#.#..##.#":
            return MazeCard.create_instance(doors=MazeCard.T_JUNCT, rotation=180)
        if line == "#.#...###":
            return MazeCard.create_instance(doors=MazeCard.T_JUNCT, rotation=270)
        if line == "#.#...#.#":
            return MazeCard.create_instance(doors=MazeCard.CROSS, rotation=0)
        return None

    for location in maze.maze_locations:
        maze[location] = create_maze_card(field(location.row, location.column))

    return maze


def maze_to_string(maze):
    """ Writes a maze as a multi-line string, as defined in create_maze() """
    def as_multi_line_string(maze_card):
        result = [
            ["#", "N", "#", ],
            ["W", ".", "E"],
            ["#", "S", "#"]
        ]
        path_to_symbol = {True: ".", False: "#"}
        result[0][1] = path_to_symbol[maze_card.has_out_path((-1, 0))]
        result[1][0] = path_to_symbol[maze_card.has_out_path((0, -1))]
        result[1][2] = path_to_symbol[maze_card.has_out_path((0, 1))]
        result[2][1] = path_to_symbol[maze_card.has_out_path((1, 0))]
        return list(map(lambda char_list: "".join(char_list), result))

    result = []
    for row in range(0, maze.maze_size):
        string_arrays = [as_multi_line_string(maze[BoardLocation(row, column)]) for column in range(0, maze.maze_size)]
        for line_part in zip(*string_arrays):
            line = "|".join(line_part)
            line = line + "|"
            result.append(line)
        result.append("-" * (maze.maze_size * 4 - 1) + "|")
    return "\n".join(result)
