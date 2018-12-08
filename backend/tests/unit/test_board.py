""" Tests for Game of model.py """
import pytest
from domain.model import Board, BoardLocation, Piece
from domain.factories import create_maze, create_random_maze, create_random_maze_card
from domain.exceptions import InvalidShiftLocationException, InvalidRotationException, \
    MoveUnreachableException, InvalidLocationException


def test_find_piece():
    """ Tests find_piece after initializing board """
    board = Board(create_random_maze())
    board.init_board([7, 14])
    assert board.find_piece(7).identifier == 7
    assert board.find_piece(14).identifier == 14


def test_init_board_sets_first_player_on_top_left_corner():
    """ Tests init_board """
    board = Board(create_random_maze())
    player_ids = [6, 18, 240, 4108]
    board.init_board(player_ids)
    assert board.find_piece(player_ids[0]).maze_card == board.maze[BoardLocation(0, 0)]


def test_init_board_sets_all_pieces_on_corners():
    """ Tests init_board """
    board = Board(create_random_maze())

    def is_corner(location):
        return (location.row in [0, board.maze.MAZE_SIZE - 1]) and (location.column in [0, board.maze.MAZE_SIZE - 1])

    player_ids = [6, 18, 240, 4108]
    board.init_board(player_ids)
    for player_id in player_ids:
        piece_location = board.maze.maze_card_location(board.find_piece(player_id).maze_card)
        assert is_corner(piece_location)


def test_init_board_gives_all_pieces_objectives():
    """ Tests init_board """
    board = Board(create_random_maze())
    player_ids = [6, 18, 240, 4108]
    board.init_board(player_ids)
    for player_id in player_ids:
        assert board.find_piece(player_id).objective_maze_card


def test_all_player_and_objective_locations_are_different():
    """ Tests init_board. """
    board = Board(create_random_maze())
    player_ids = [6, 18, 240, 4108]
    board.init_board(player_ids)
    _assert_all_piece_and_objective_locations_different(board)


def test_objective_locations_after_reaching_location():
    """ Tests new objective generation after reaching one """
    board = Board(maze=create_maze(MAZE_STRING), leftover_card=create_random_maze_card())
    player_id = 0
    board._pieces = [Piece(player_id)]
    player = board.find_piece(player_id)
    player.maze_card = board.maze[BoardLocation(0, 6)]
    player.objective_maze_card = board.maze[BoardLocation(1, 6)]
    board.move(player_id, BoardLocation(1, 6))
    _assert_all_piece_and_objective_locations_different(board)


def _assert_all_piece_and_objective_locations_different(board):
    """ asserts for a given Board instance """
    card_ids = set()
    for piece in board.pieces:
        card_ids.add(piece.maze_card.identifier)
        card_ids.add(piece.objective_maze_card.identifier)
    assert len(card_ids) == len(board.pieces) * 2


def test_shift_updates_old_leftover_rotation():
    """ Tests shift """
    board = Board()
    player_id = 7
    board.init_board([player_id])
    old_leftover = board.leftover_card
    board.shift(player_id, BoardLocation(0, 1), 270)
    assert old_leftover.rotation == 270


def test_shift_updates_new_leftover():
    """ Tests shift """
    board = Board()
    player_id = 7
    board.init_board([player_id])
    pushed_out = board.maze[BoardLocation(board.maze.MAZE_SIZE - 1, 1)]
    board.shift(player_id, BoardLocation(0, 1), 270)
    assert pushed_out == board.leftover_card


def test_shift_updates_pieces_on_pushed_out_card():
    """ Tests shift """
    board = Board()
    player_id = 7
    board.init_board([player_id])
    piece = board.find_piece(player_id)
    pushed_card = board.leftover_card
    piece.maze_card = board.maze[BoardLocation(0, 3)]
    board.shift(player_id, BoardLocation(board.maze.MAZE_SIZE-1, 3), 90)
    assert piece.maze_card == pushed_card


def test_shift_raises_error_on_invalid_location():
    """ Tests shift validation """
    board = Board()
    player_id = 7
    board.init_board([player_id])
    with pytest.raises(InvalidShiftLocationException):
        board.shift(player_id, BoardLocation(0, 0), 90)


def test_shift_raises_error_on_invalid_rotation():
    """ Tests shift validation """
    board = Board()
    player_id = 7
    board.init_board([player_id])
    with pytest.raises(InvalidRotationException):
        board.shift(player_id, BoardLocation(0, 1), 70)


def test_move_updates_players_maze_card_correctly():
    """ Tests move
    Instead of calling init_board(), the board is built manually, and
    the player's position is set manually as well, so that
    randomness is eliminated for testing """
    board = Board(maze=create_maze(MAZE_STRING), leftover_card=create_random_maze_card())
    player_id = 0
    board._pieces = [Piece(player_id)]
    board.find_piece(player_id).maze_card = board.maze[BoardLocation(0, 1)]
    board.move(player_id, BoardLocation(0, 2))
    assert board.maze[BoardLocation(0, 2)] == board.find_piece(player_id).maze_card


def test_move_raises_error_on_unreachable_location():
    """ Tests move validation """
    board = Board(maze=create_maze(MAZE_STRING), leftover_card=create_random_maze_card())
    player_id = 0
    board._pieces = [Piece(player_id)]
    board.find_piece(player_id).maze_card = board.maze[BoardLocation(0, 1)]
    with pytest.raises(MoveUnreachableException):
        board.move(player_id, BoardLocation(0, 0))


def test_move_raises_error_on_invalid_location():
    """ Tests move validation """
    board = Board()
    player_id = 7
    board.init_board([player_id])
    with pytest.raises(InvalidLocationException):
        board.move(player_id, BoardLocation(-1, -1))



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
