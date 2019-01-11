""" Tests for Game of game.py """
import pytest
from server.model.game import Board, BoardLocation
from server.model.factories import create_maze, create_random_maze, create_random_maze_card
from server.model.exceptions import InvalidShiftLocationException, InvalidRotationException, \
    MoveUnreachableException, InvalidLocationException


def test_create_piece_sets_all_pieces_on_corners():
    """ Tests create_piece """
    board = Board(create_random_maze())

    def is_corner(location):
        return (location.row in [0, board.maze.MAZE_SIZE - 1]) and (location.column in [0, board.maze.MAZE_SIZE - 1])

    for _ in range(8):
        piece = board.create_piece()
        piece_location = board.maze.maze_card_location(piece.maze_card)
        assert is_corner(piece_location)


def test_remove_piece_after_create_piece():
    """ Tests remove_piece """
    board = Board(create_random_maze())
    piece = board.create_piece()
    board.remove_piece(piece)
    assert not board.pieces


def test_after_series_of_creates_and_removes_no_corners_empty():
    """ Tests create_piece. Adds three pieces, removes two, adds three,
    and checks that all pieces are on a different corner """
    board = Board(create_random_maze())
    piece1 = board.create_piece()
    piece2 = board.create_piece()
    board.create_piece()
    board.remove_piece(piece1)
    board.remove_piece(piece2)
    board.create_piece()
    board.create_piece()
    board.create_piece()
    assert len(board.pieces) == 4
    piece_cards = set()
    for piece in board.pieces:
        piece_cards.add(piece.maze_card)
    assert len(piece_cards) == 4


def test_clear_pieces_after_creations_empties_pieces():
    """ Tests clear_pieces. """
    board = Board(create_random_maze())
    for _ in range(8):
        board.create_piece()
    assert len(board.pieces) == 8
    board.clear_pieces()
    assert not board.pieces


def test_move_new_objective_locations_after_reaching_location():
    """ Tests new objective generation after reaching one """
    maze = create_maze(MAZE_STRING)
    objective_maze_card = maze[BoardLocation(1, 6)]
    board = Board(
        maze=maze,
        leftover_card=create_random_maze_card(),
        objective_maze_card=objective_maze_card)
    piece = board.create_piece()
    piece.maze_card = maze[BoardLocation(0, 6)]
    board.move(piece, BoardLocation(1, 6))
    _assert_all_piece_and_objective_location_different(board)


def _assert_all_piece_and_objective_location_different(board):
    """ asserts for a given Board instance """
    card_ids = set()
    for piece in board.pieces:
        card_ids.add(piece.maze_card.identifier)
    card_ids.add(board.objective_maze_card.identifier)
    assert len(card_ids) == len(board.pieces) + 1


def test_shift_updates_old_leftover_rotation():
    """ Tests shift """
    board = Board()
    old_leftover = board.leftover_card
    board.shift(BoardLocation(0, 1), 270)
    assert old_leftover.rotation == 270


def test_shift_updates_new_leftover():
    """ Tests shift """
    board = Board()
    pushed_out = board.maze[BoardLocation(board.maze.MAZE_SIZE - 1, 1)]
    board.shift(BoardLocation(0, 1), 270)
    assert pushed_out == board.leftover_card


def test_shift_updates_pieces_on_pushed_out_card():
    """ Tests shift """
    board = Board()
    piece = board.create_piece()
    pushed_card = board.leftover_card
    piece.maze_card = board.maze[BoardLocation(0, 3)]
    board.shift(BoardLocation(board.maze.MAZE_SIZE-1, 3), 90)
    assert piece.maze_card == pushed_card


def test_shift_raises_error_on_invalid_location():
    """ Tests shift validation """
    board = Board()
    with pytest.raises(InvalidShiftLocationException):
        board.shift(BoardLocation(0, 0), 90)


def test_shift_raises_error_on_invalid_rotation():
    """ Tests shift validation """
    board = Board()
    with pytest.raises(InvalidRotationException):
        board.shift(BoardLocation(0, 1), 70)


def test_move_updates_players_maze_card_correctly():
    """ Tests move
    Instead of calling init_board(), the board is built manually, and
    the player's position is set manually as well, so that
    randomness is eliminated for testing """
    board = Board(maze=create_maze(MAZE_STRING), leftover_card=create_random_maze_card())
    piece = board.create_piece()
    piece.maze_card = board.maze[BoardLocation(0, 1)]
    board.move(piece, BoardLocation(0, 2))
    assert board.maze[BoardLocation(0, 2)] == piece.maze_card


def test_move_raises_error_on_unreachable_location():
    """ Tests move validation """
    board = Board(maze=create_maze(MAZE_STRING), leftover_card=create_random_maze_card())
    piece = board.create_piece()
    piece.maze_card = board.maze[BoardLocation(0, 1)]
    with pytest.raises(MoveUnreachableException):
        board.move(piece, BoardLocation(0, 0))


def test_move_raises_error_on_invalid_location():
    """ Tests move validation """
    board = Board()
    piece = board.create_piece()
    with pytest.raises(InvalidLocationException):
        board.move(piece, BoardLocation(-1, -1))


def test_opposing_insert_location_for_east_location():
    """ Tests opposing_insert_location """
    board = Board()
    size = board.maze.MAZE_SIZE
    assert board.opposing_insert_location(BoardLocation(5, size-1)) == BoardLocation(5, 0)


def test_opposing_insert_location_for_south_location():
    """ Tests opposing_insert_location """
    board = Board()
    size = board.maze.MAZE_SIZE
    assert board.opposing_insert_location(BoardLocation(size-1, 3)) == BoardLocation(0, 3)

def test_opposing_insert_location_for_west_location():
    """ Tests opposing_insert_location """
    board = Board()
    size = board.maze.MAZE_SIZE
    assert board.opposing_insert_location(BoardLocation(1, 0)) == BoardLocation(1, size-1)


MAZE_STRING = """
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
