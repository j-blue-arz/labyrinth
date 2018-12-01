""" Tests for MoveValidator. A Board instance is created from a string representation of a labyrinth.
Several validation tests are performed on this instance """

from domain.model import Board, MazeCard, BoardLocation
from domain.validation import MoveValidator


def test_validate_move_for_same_location():
    """ Tests validate_move """
    board = create_board(BOARD_STRING)
    validator = MoveValidator(board)
    assert validator.validate_move(BoardLocation(0, 0), BoardLocation(0, 0))


def test_validate_move_for_unconnected_neighbors():
    """ Tests validate_move """
    board = create_board(BOARD_STRING)
    validator = MoveValidator(board)
    assert not validator.validate_move(BoardLocation(0, 0), BoardLocation(1, 0))
    assert not validator.validate_move(BoardLocation(0, 0), BoardLocation(0, 1))
    assert not validator.validate_move(BoardLocation(2, 4), BoardLocation(2, 5))


def test_validate_move_for_connected_neighbors():
    """ Tests validate_move """
    board = create_board(BOARD_STRING)
    validator = MoveValidator(board)
    assert validator.validate_move(BoardLocation(2, 4), BoardLocation(1, 4))
    assert validator.validate_move(BoardLocation(2, 4), BoardLocation(2, 3))
    assert validator.validate_move(BoardLocation(2, 4), BoardLocation(3, 4))


def test_validate_move_for_connected_neighbors_wo_direct_path():
    """ Tests validate_move """
    board = create_board(BOARD_STRING)
    validator = MoveValidator(board)
    assert validator.validate_move(BoardLocation(3, 1), BoardLocation(3, 2))


def test_validate_move_for_connected_distant_cards():
    """ Tests validate_move """
    board = create_board(BOARD_STRING)
    validator = MoveValidator(board)
    assert validator.validate_move(BoardLocation(1, 4), BoardLocation(5, 0))


def test_validate_move_for_unconnected_cards_with_only_one_wall():
    """ Tests validate_move """
    board = create_board(BOARD_STRING)
    validator = MoveValidator(board)
    assert not validator.validate_move(BoardLocation(1, 0), BoardLocation(4, 4))


def test_validate_move_for_paths_on_border():
    """ Tests validate_move """
    board = create_board(BOARD_STRING)
    validator = MoveValidator(board)
    assert validator.validate_move(BoardLocation(5, 0), BoardLocation(6, 3))
    assert validator.validate_move(BoardLocation(0, 6), BoardLocation(2, 6))


def test_validate_move_for_swapped_locations():
    """ Tests validate_move """
    board = create_board(BOARD_STRING)
    validator = MoveValidator(board)
    assert not validator.validate_move(BoardLocation(1, 0), BoardLocation(0, 0))
    assert not validator.validate_move(BoardLocation(0, 1), BoardLocation(0, 0))
    assert not validator.validate_move(BoardLocation(2, 5), BoardLocation(2, 4))

    assert validator.validate_move(BoardLocation(1, 4), BoardLocation(2, 4))
    assert validator.validate_move(BoardLocation(2, 3), BoardLocation(2, 4))
    assert validator.validate_move(BoardLocation(3, 4), BoardLocation(2, 4))

    assert validator.validate_move(BoardLocation(3, 2), BoardLocation(3, 1))

    assert validator.validate_move(BoardLocation(5, 0), BoardLocation(1, 4))

    assert not validator.validate_move(BoardLocation(4, 4), BoardLocation(1, 0))

    assert validator.validate_move(BoardLocation(6, 3), BoardLocation(5, 0))
    assert validator.validate_move(BoardLocation(2, 6), BoardLocation(0, 6))


def create_board(board_string):
    """ Reads a multi-line string representing a labyrinth configuration.
    Each maze card is a 3*3 substring of this multiline string. Walls are represented by '#',
    paths with '.'. After each field, there is one delimiter symbol, both horizontally and vertically.
    First line starts at index 1."""
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

    board = Board()
    for location in board.board_locations():
        board[location] = create_maze_card(field(location.row, location.column))
    return board


BOARD_STRING = """
###|#.#|#.#|###|#.#|#.#|###|
#..|#..|...|...|#..|..#|..#|
#.#|###|###|#.#|###|###|#.#|
---------------------------|
###|###|#.#|#.#|#.#|#.#|#.#|
...|...|#.#|#..|#.#|...|..#|
#.#|#.#|#.#|###|#.#|###|#.#|
---------------------------|
#.#|#.#|#.#|#.#|#.#|#.#|#.#|
#..|#..|..#|#..|..#|#.#|..#|
#.#|#.#|#.#|#.#|#.#|#.#|#.#|
---------------------------|
#.#|#.#|#.#|###|#.#|###|###|
..#|..#|#..|...|...|...|..#|
###|#.#|###|#.#|###|#.#|#.#|
---------------------------|
###|#.#|###|#.#|###|#.#|###|
#..|..#|#..|#.#|...|#..|...|
#.#|###|#.#|#.#|#.#|###|###|
---------------------------|
###|#.#|###|#.#|#.#|#.#|#.#|
..#|#..|...|...|#.#|#..|..#|
#.#|#.#|###|###|#.#|#.#|#.#|
---------------------------|
#.#|#.#|###|###|#.#|#.#|#.#|
#..|...|...|...|#.#|...|..#|
###|###|#.#|###|#.#|###|###|
---------------------------*

"""
