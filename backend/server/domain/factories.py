""" This module contains methods to build and initialize model objects """
from random import choice
from .model import MazeCard, Maze, BoardLocation, Board, Game


def create_random_maze_card():
    """ Creates a new instance of MazeCard with
    random doors and rotation
    """
    doors = choice([MazeCard.STRAIGHT, MazeCard.CORNER, MazeCard.T_JUNCT])
    rotation = choice([0, 90, 180, 270])
    return MazeCard.create_instance(doors, rotation)


def create_random_maze():
    """ Generates a random maze state.
    Corners of the maze are fixed as corners,
    Other unshiftable border pieces are t-junctions.
    """
    MazeCard.reset_ids()
    maze = Maze()
    fixed_cards = {
        BoardLocation(0, 0): MazeCard(doors=MazeCard.CORNER, rotation=90),
        BoardLocation(0, Maze.MAZE_SIZE - 1): MazeCard(doors=MazeCard.CORNER, rotation=180),
        BoardLocation(Maze.MAZE_SIZE - 1, Maze.MAZE_SIZE - 1): MazeCard(doors=MazeCard.CORNER, rotation=270),
        BoardLocation(Maze.MAZE_SIZE - 1, 0): MazeCard(doors=MazeCard.CORNER, rotation=0)}

    def card_at(location):
        if location in fixed_cards:
            return MazeCard.create_instance(fixed_cards[location].doors, fixed_cards[location].rotation)
        return create_random_maze_card()

    for location in Maze.maze_locations():
        maze[location] = card_at(location)
    return maze


def create_board():
    """ Creates a Board instance. Random maze, random left over. """
    return Board(maze=create_random_maze(), leftover_card=create_random_maze_card())


def create_game():
    """ Creates a game instance with a random board. Player and piece initialization
    is not done here, but dynamically depending on the number of players """
    return Game(create_board())


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
