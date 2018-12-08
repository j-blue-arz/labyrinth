""" This module defines a convenient way to create maze layouts
by calling the function create_maze on a multiline string."""

from domain.model import Maze, MazeCard


def create_maze(maze_string):
    """ Creates a maze, fills it by a string and returns the Maze """
    maze = Maze()
    fill_maze(maze_string, maze)
    return maze


def fill_maze(maze_string, maze):
    """ Reads a multi-line string representing a labyrinth configuration.
    Each maze card is a 3*3 substring of this multiline string. Walls are represented by '#',
    paths with '.'. After each field, there is one delimiter symbol, both horizontally and vertically.
    First line starts at index 1. """
    lines = maze_string.splitlines()[1:]

    def field(row, col):
        row_lines = lines[row*4:row*4 + 3]
        field_lines = [row_line[col*4:col*4+3] for row_line in row_lines]
        return field_lines

    def create_maze_card(field):
        line = "".join(field)
        if line == "###...###":
            return MazeCard.generate_random(doors=MazeCard.STRAIGHT, rotation=90)
        if line == "#.##.##.#":
            return MazeCard.generate_random(doors=MazeCard.STRAIGHT, rotation=180)
        if line == "#.##..###":
            return MazeCard.generate_random(doors=MazeCard.CORNER, rotation=0)
        if line == "####..#.#":
            return MazeCard.generate_random(doors=MazeCard.CORNER, rotation=90)
        if line == "###..##.#":
            return MazeCard.generate_random(doors=MazeCard.CORNER, rotation=180)
        if line == "#.#..####":
            return MazeCard.generate_random(doors=MazeCard.CORNER, rotation=270)
        if line == "#.##..#.#":
            return MazeCard.generate_random(doors=MazeCard.T_JUNCT, rotation=0)
        if line == "###...#.#":
            return MazeCard.generate_random(doors=MazeCard.T_JUNCT, rotation=90)
        if line == "#.#..##.#":
            return MazeCard.generate_random(doors=MazeCard.T_JUNCT, rotation=180)
        if line == "#.#...###":
            return MazeCard.generate_random(doors=MazeCard.T_JUNCT, rotation=270)
        return None

    for location in maze.maze_locations():
        maze[location] = create_maze_card(field(location.row, location.column))
