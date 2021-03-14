""" Tests for Game of game.py """
import pytest
from tests.unit.factories import create_random_maze, MazeCardFactory
from labyrinth.model.game import Board, BoardLocation
from labyrinth.model.factories import create_maze
from labyrinth.model.exceptions import InvalidShiftLocationException, InvalidRotationException, \
    MoveUnreachableException, InvalidLocationException


def test_create_piece_sets_all_pieces_on_corners():
    """ Tests create_piece """
    board = Board(create_random_maze())

    def is_corner(location):
        return (location.row in [0, board.maze.maze_size - 1]) and (location.column in [0, board.maze.maze_size - 1])

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
    piece_cards = {piece.maze_card for piece in board.pieces}
    assert len(piece_cards) == 4


def test_create_piece_assigns_pieces_consecutive_unique_indices():
    """ Tests create_piece. Adds four pieces, removes first two, adds one, removes third, adds two,
    and checks that all pieces have consecutive unique index """
    board = Board(create_random_maze())
    pieces = [board.create_piece(), board.create_piece(), board.create_piece(), board.create_piece()]
    board.remove_piece(pieces[0])
    board.remove_piece(pieces[1])
    pieces[0] = board.create_piece()
    board.remove_piece(pieces[3])
    pieces[1] = board.create_piece()
    pieces[3] = board.create_piece()
    assert set([0, 1, 2, 3]) == set(map(lambda piece: piece.piece_index, pieces))


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
    maze_card_factory = MazeCardFactory()
    maze = create_maze(MAZE_STRING, maze_card_factory)
    objective_maze_card = maze[BoardLocation(1, 6)]
    board = Board(
        maze=maze,
        leftover_card=maze_card_factory.create_random_maze_card(),
        objective_maze_card=objective_maze_card)
    piece = board.create_piece()
    piece.maze_card = maze[BoardLocation(0, 6)]
    board.move(piece, BoardLocation(1, 6))
    _assert_all_piece_and_objective_location_different(board)


def _assert_all_piece_and_objective_location_different(board):
    """ asserts for a given Board instance """
    card_ids = {piece.maze_card.identifier for piece in board.pieces}
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
    pushed_out = board.maze[BoardLocation(board.maze.maze_size - 1, 1)]
    board.shift(BoardLocation(0, 1), 270)
    assert pushed_out == board.leftover_card


def test_shift_updates_pieces_on_pushed_out_card():
    """ Tests shift """
    board = Board()
    piece = board.create_piece()
    pushed_card = board.leftover_card
    piece.maze_card = board.maze[BoardLocation(0, 3)]
    board.shift(BoardLocation(board.maze.maze_size-1, 3), 90)
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
    maze_card_factory = MazeCardFactory()
    board = Board(maze=create_maze(MAZE_STRING, maze_card_factory),
                  leftover_card=maze_card_factory.create_random_maze_card())
    piece = board.create_piece()
    piece.maze_card = board.maze[BoardLocation(0, 1)]
    board.move(piece, BoardLocation(0, 2))
    assert board.maze[BoardLocation(0, 2)] == piece.maze_card


def test_move_raises_error_on_unreachable_location():
    """ Tests move validation """
    maze_card_factory = MazeCardFactory()
    board = Board(maze=create_maze(MAZE_STRING, maze_card_factory),
                  leftover_card=maze_card_factory.create_random_maze_card())
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


def test_opposing_border_location_for_east_location():
    """ Tests opposing_border_location """
    board = Board()
    size = board.maze.maze_size
    assert board.opposing_border_location(BoardLocation(5, size-1)) == BoardLocation(5, 0)


def test_opposing_border_location_for_south_location():
    """ Tests opposing_border_location """
    board = Board()
    size = board.maze.maze_size
    assert board.opposing_border_location(BoardLocation(size-1, 3)) == BoardLocation(0, 3)


def test_opposing_border_location_for_west_location():
    """ Tests opposing_border_location """
    board = Board()
    size = board.maze.maze_size
    assert board.opposing_border_location(BoardLocation(1, 0)) == BoardLocation(1, size-1)


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
