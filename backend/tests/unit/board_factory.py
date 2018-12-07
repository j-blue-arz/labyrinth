""" This module defines a convenient way to create maze board layouts
by calling the function create_board on a multiline string."""

from domain.model import Board, MazeCard


def create_board(board_string):
    """ Creates a board, fills it by a string and returns the Board """
    board = Board()
    fill_board(board_string, board)
    return board


def fill_board(board_string, board):
    """ Reads a multi-line string representing a labyrinth configuration.
    Each maze card is a 3*3 substring of this multiline string. Walls are represented by '#',
    paths with '.'. After each field, there is one delimiter symbol, both horizontally and vertically.
    First line starts at index 1. """
    lines = board_string.splitlines()[1:]

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

    for location in board.board_locations():
        board[location] = create_maze_card(field(location.row, location.column))
