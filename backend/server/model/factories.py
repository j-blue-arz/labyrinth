""" This module contains methods to build and initialize model objects """
import random
from .game import MazeCard, Maze, BoardLocation, Board, Game


def create_random_maze_card(doors=None):
    """ Creates a new instance of MazeCard with
    random doors and rotation
    """
    if not doors:
        doors = random.choice([MazeCard.STRAIGHT, MazeCard.CORNER, MazeCard.T_JUNCT])
    rotation = random.choice([0, 90, 180, 270])
    return MazeCard.create_instance(doors, rotation)


def create_random_maze():
    """ Generates a random maze state.
    Corners of the maze are fixed as corners,
    """
    fixed_cards = {
        BoardLocation(0, 0): MazeCard(doors=MazeCard.CORNER, rotation=90),
        BoardLocation(0, 6): MazeCard(doors=MazeCard.CORNER, rotation=180),
        BoardLocation(6, 6): MazeCard(doors=MazeCard.CORNER, rotation=270),
        BoardLocation(6, 0): MazeCard(doors=MazeCard.CORNER, rotation=0)}

    MazeCard.reset_ids()
    maze = Maze()

    def card_at(location):
        if location in fixed_cards:
            return MazeCard.create_instance(fixed_cards[location].doors, fixed_cards[location].rotation)
        return create_random_maze_card()

    for location in Maze.maze_locations():
        maze[location] = card_at(location)
    return maze


def create_random_original_maze_and_leftover():
    """ Generates a random maze state according to the rules of the original game.
    Corners of the maze are fixed as corners,
    All other fixed maze cards are t-junctions
    15 corners, 6 t-junctions, and 13 straights are randomly placed on the board
    """
    fixed_cards = {
        BoardLocation(0, 0): MazeCard(doors=MazeCard.CORNER, rotation=90),
        BoardLocation(0, 6): MazeCard(doors=MazeCard.CORNER, rotation=180),
        BoardLocation(6, 6): MazeCard(doors=MazeCard.CORNER, rotation=270),
        BoardLocation(6, 0): MazeCard(doors=MazeCard.CORNER, rotation=0),
        BoardLocation(0, 2): MazeCard(doors=MazeCard.T_JUNCT, rotation=90),
        BoardLocation(0, 4): MazeCard(doors=MazeCard.T_JUNCT, rotation=90),
        BoardLocation(2, 6): MazeCard(doors=MazeCard.T_JUNCT, rotation=180),
        BoardLocation(4, 6): MazeCard(doors=MazeCard.T_JUNCT, rotation=180),
        BoardLocation(6, 2): MazeCard(doors=MazeCard.T_JUNCT, rotation=270),
        BoardLocation(6, 4): MazeCard(doors=MazeCard.T_JUNCT, rotation=270),
        BoardLocation(2, 0): MazeCard(doors=MazeCard.T_JUNCT, rotation=0),
        BoardLocation(4, 0): MazeCard(doors=MazeCard.T_JUNCT, rotation=0),
        BoardLocation(2, 2): MazeCard(doors=MazeCard.T_JUNCT, rotation=0),
        BoardLocation(2, 4): MazeCard(doors=MazeCard.T_JUNCT, rotation=90),
        BoardLocation(4, 4): MazeCard(doors=MazeCard.T_JUNCT, rotation=180),
        BoardLocation(4, 2): MazeCard(doors=MazeCard.T_JUNCT, rotation=270)}

    MazeCard.reset_ids()
    maze = Maze()
    loose_cards_doors = [MazeCard.CORNER]*15 + [MazeCard.T_JUNCT]*6 + [MazeCard.STRAIGHT]*13
    loose_cards = [create_random_maze_card(doors=doors) for doors in loose_cards_doors]
    random.shuffle(loose_cards)
    card_iter = iter(loose_cards)

    for location in Maze.maze_locations():
        if location in fixed_cards:
            maze[location] = MazeCard.create_instance(fixed_cards[location].doors, fixed_cards[location].rotation)
        else:
            maze[location] = card_iter.__next__()

    leftover = card_iter.__next__()
    return maze, leftover


def create_board():
    """ Creates a Board instance. Random maze, random leftover. """
    return Board(maze=create_random_maze(), leftover_card=create_random_maze_card())


def create_original_board():
    """ Creates a Board instance. Original maze, original random leftover """
    maze, leftover = create_random_original_maze_and_leftover()
    return Board(maze=maze, leftover_card=leftover)


def create_game(original=False):
    """ Creates a game instance with a random board. Player and piece initialization
    is not done here, but dynamically depending on the number of players """
    if original:
        return Game(0, board=create_original_board())
    return Game(0, board=create_board())


def create_maze(maze_string):
    """ Reads a multi-line string representing a labyrinth configuration.
    Each maze card is a 3*3 substring of this multiline string. Walls are represented by '#',
    paths with '.'. After each field, there is one delimiter symbol, both horizontally and vertically.
    First line starts at index 1. """
    maze = Maze()

    lines = maze_string.splitlines()[1:]

    def field(row, col):
        row_lines = lines[row*4:row*4 + 3]
        field_lines = [row_line[col*4:col*4+3] for row_line in row_lines]
        return field_lines

    def create_maze_card(field):
        line = "".join(field)
        if line == "###...###":
            return MazeCard.create_instance(doors=MazeCard.STRAIGHT, rotation=90)
        if line == "#.##.##.#":
            return MazeCard.create_instance(doors=MazeCard.STRAIGHT, rotation=180)
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
        return None

    for location in maze.maze_locations():
        maze[location] = create_maze_card(field(location.row, location.column))

    return maze
