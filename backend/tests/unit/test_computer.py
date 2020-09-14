""" Tests for module computer in model. The classes contained in this are multithreaded.
The tests only run these classes in a single thread, by calling run() directly. """
import copy
from unittest.mock import Mock, patch, PropertyMock

import pytest

from labyrinth.model.computer import ComputerPlayer, RandomActionsMethod, create_computer_player
from labyrinth.model.factories import create_maze, MazeCardFactory
from labyrinth.model.game import Board, BoardLocation, Game


def test_create_computer_player_fetches_urls_from_url_supplier():
    """ Uses the create_computer_player to create a ComputerPlayer
    with the url_supplier parameter, and expects
    that the factory method calls methods on the url_supplier """
    url_supplier = Mock()
    url_supplier.get_shift_url.return_value = "shift-url"
    url_supplier.get_move_url.return_value = "move-url"
    game = Mock()
    type(game).identifier = PropertyMock(return_value=7)
    player = create_computer_player(player_id=9, compute_method="random", url_supplier=url_supplier, game=game)
    url_supplier.get_shift_url.assert_called_once_with(7, 9)
    url_supplier.get_move_url.assert_called_once_with(7, 9)
    assert player.shift_url == "shift-url"
    assert player.move_url == "move-url"

    url_supplier.reset_mock()
    player = create_computer_player(player_id=17, compute_method="random", url_supplier=url_supplier)
    url_supplier.get_shift_url.assert_not_called()
    url_supplier.get_move_url.assert_not_called()

    player.set_game(game)
    url_supplier.get_shift_url.assert_called_once_with(7, 17)
    url_supplier.get_move_url.assert_called_once_with(7, 17)
    assert player.shift_url == "shift-url"
    assert player.move_url == "move-url"


def test_computer_player_register_in_turns():
    """ Tests that register_in_turns calls method in turns with callback """
    turns = Mock()
    player = ComputerPlayer(compute_method_factory=RandomActionsMethod, shift_url="shift-url",
                            move_url="move-url", game=None, identifier=9)
    player.register_in_turns(turns)
    turns.add_player.assert_called_once_with(player, turn_callback=player.start)


@patch('time.sleep', return_value=None)
@patch.object(RandomActionsMethod, "start", autospec=True, side_effect=RandomActionsMethod.run)
@patch.object(ComputerPlayer, "_post_shift")
@patch.object(ComputerPlayer, "_post_move")
def test_computer_player_calls_start_on_compute_method(post_move, post_shift, compute_method_start, time_sleep):
    """ Tests that the computer player calls start() one its computation method.
    .start() is patched so that the computation method runs sequentially.
    """
    card_factory = MazeCardFactory()
    board = Board(create_maze(MAZE_STRING, card_factory), leftover_card=card_factory.create_instance("NE", 0))
    piece = board.create_piece()
    game = Mock()
    type(game).identifier = PropertyMock(return_value=7)
    game.get_enabled_shift_locations.return_value = board.shift_locations
    player = ComputerPlayer(compute_method_factory=RandomActionsMethod, move_url="move-url", shift_url="shift-url",
                            game=game, identifier=9, board=board, piece=piece)
    player.run()
    compute_method_start.assert_called_once()
    post_shift.assert_called_once()
    post_move.assert_called_once()
    shift_location, rotation = post_shift.call_args[0]
    move_location = post_move.call_args[0][0]
    assert rotation in [0, 90, 180, 270]
    assert shift_location in board.shift_locations
    assert move_location in board.maze.maze_locations


def test_random_actions_computes_valid_actions():
    """ Runs computation 100 times and expects that it returns valid actions in each run """
    card_factory = MazeCardFactory()
    orig_board = Board(create_maze(MAZE_STRING, card_factory), leftover_card=card_factory.create_instance("NE", 0))
    for _ in range(100):
        board = copy.deepcopy(orig_board)
        maze = board.maze
        piece = board.create_piece()
        piece.maze_card = maze[BoardLocation(0, 0)]
        game = Mock()
        game.get_enabled_shift_locations.return_value = board.shift_locations
        compute_method = RandomActionsMethod(board, piece, game)
        assert compute_method.shift_action is None
        assert compute_method.move_action is None
        compute_method.run()
        shift_location, shift_rotation = compute_method.shift_action
        move_location = compute_method.move_action
        assert shift_rotation in [0, 90, 180, 270]
        assert shift_location in board.shift_locations
        allowed_coordinates = [(0, 0)]
        if shift_location == BoardLocation(0, 1) and shift_rotation == 270:
            allowed_coordinates += [(0, 1)]
        elif shift_location == BoardLocation(0, 1) and shift_rotation == 180:
            allowed_coordinates += [(0, 1), (1, 1)]
        elif shift_location == BoardLocation(1, 0) and shift_rotation == 270:
            allowed_coordinates += [(1, 0)]
        elif shift_location == BoardLocation(1, 0) and shift_rotation == 0:
            allowed_coordinates += [(1, 0), (1, 1), (1, 2), (2, 1), (2, 2), (3, 1), (3, 2)]
        elif shift_location == BoardLocation(6, 1):
            allowed_coordinates += [(0, 1), (0, 2), (1, 1), (2, 1)]
        allowed_moves = {
            BoardLocation(*coordinates) for coordinates in allowed_coordinates
        }

        assert move_location in allowed_moves


@pytest.mark.skip("test can fail")
def test_random_actions_should_have_different_results():
    """ Runs random actions method 200 times and checks that a certain move is performed sooner or later.
    One run has a possibilty of 1/(12*4*8) + 1/(12*4) to succeed.
    This test has a probability of about 0.008 to fail. """
    card_factory = MazeCardFactory()
    orig_board = Board(create_maze(MAZE_STRING, card_factory), leftover_card=card_factory.create_instance("NE", 0))
    move_locations = set()
    for _ in range(200):
        board = copy.deepcopy(orig_board)
        maze = board.maze
        piece = board.create_piece()
        piece.maze_card = maze[BoardLocation(0, 0)]
        game = Mock()
        game.get_enabled_shift_locations.return_value = board.shift_locations
        compute_method = RandomActionsMethod(board, piece, game)
        compute_method.run()
        move_locations.add(compute_method.move_action)
    assert BoardLocation(2, 1) in move_locations


@patch('time.sleep', return_value=None)
@patch.object(RandomActionsMethod, "start", autospec=True, side_effect=RandomActionsMethod.run)
@patch.object(ComputerPlayer, "_post_shift")
@patch.object(ComputerPlayer, "_post_move")
def test_computer_player_random_algorith_when_piece_is_pushed_out(post_move, post_shift, method_start, time_sleep):
    """ Tests case where piece is positioned on a shift location, so that it is pushed out.
    Runs computation 100 times. Push-out expectation rate is 1/12.
    Probability that no push-out takes place in 100 runs is negligible
    .start() is patched so that the compute method runs sequentially.
    This test recreates a bug, where the pushed-out piece is not updated correctly, leading
    to exceptions thrown when computer makes a move.
    """
    card_factory = MazeCardFactory()
    board = Board(create_maze(MAZE_STRING, card_factory), leftover_card=card_factory.create_instance("NE", 0))
    piece = board.create_piece()
    piece.maze_card = board.maze[BoardLocation(3, 6)]
    game = Mock()
    game.get_enabled_shift_locations.return_value = board.shift_locations
    player = ComputerPlayer(compute_method_factory=RandomActionsMethod, move_url="move-url", shift_url="shift-url",
                            game=game, identifier=9, board=board, piece=piece)
    for _ in range(100):
        player.run()
        shift_location, _ = post_shift.call_args[0]
        move_location = post_move.call_args[0][0]
        allowed_coordinates = [(3, 6)]
        if shift_location == BoardLocation(3, 6):
            allowed_coordinates = [(3, 5)]
        elif shift_location == BoardLocation(3, 0):
            allowed_coordinates = [(3, 0)]
        allowed_moves = {BoardLocation(*coordinates) for coordinates in allowed_coordinates}
        assert move_location in allowed_moves


def test_random_actions_should_respect_no_pushback_rule():
    """ Runs computation 50 times and checks that none of the computed shifts reverts the previous shift action """

    card_factory = MazeCardFactory()
    orig_board = Board(create_maze(MAZE_STRING, card_factory), leftover_card=card_factory.create_instance("NE", 0))
    for _ in range(50):
        board = copy.deepcopy(orig_board)
        maze = board.maze
        piece = board.create_piece()
        piece.maze_card = maze[BoardLocation(0, 0)]
        game = Game(0, board=orig_board)
        game.previous_shift_location = BoardLocation(0, 3)
        compute_method = RandomActionsMethod(board, piece, game)
        compute_method.run()
        shift_location, _ = compute_method.shift_action
        assert shift_location != BoardLocation(6, 3)


@patch('time.sleep', return_value=None)
@patch.object(RandomActionsMethod, "start", autospec=True, side_effect=RandomActionsMethod.run)
@patch.object(ComputerPlayer, "_post_shift")
@patch.object(ComputerPlayer, "_post_move")
def test_computer_player_random_algorith_respects_no_pushback_rule(post_move, post_shift, method_start, time_sleep):
    """ Tests case where a previous shift cannot be reversed
    Runs computation 100 times. No shift should reverse previous shift.
    .start() is patched so that the computation runs sequentially.
    This test recreates a bug, where the compute method was not informed of the previous shift,
    leading to invalid shift actions.
    """
    card_factory = MazeCardFactory()
    board = Board(create_maze(MAZE_STRING, card_factory), leftover_card=card_factory.create_instance("NE", 0))
    piece = board.create_piece()
    previous_shift_location = BoardLocation(6, 1)
    game = Mock()
    game.get_enabled_shift_locations.return_value = board.shift_locations.difference({previous_shift_location})
    type(game).identifier = PropertyMock(return_value=7)
    piece.maze_card = board.maze[BoardLocation(3, 6)]
    player = ComputerPlayer(compute_method_factory=RandomActionsMethod, move_url="move-url", shift_url="shift-url",
                            game=game, identifier=9, board=board, piece=piece)
    for _ in range(100):
        player.run()
        shift_location, _ = post_shift.call_args[0]
        assert shift_location != BoardLocation(6, 1)


MAZE_STRING = """
###|#.#|#.#|###|#.#|#.#|###|
#..|#..|..#|...|#..|..#|..#|
#.#|###|###|#.#|###|###|#.#|
---------------------------|
###|###|#.#|#.#|#.#|#.#|#.#|
...|...|#.#|#..|#.#|...|..#|
#.#|#.#|#.#|###|#.#|###|#.#|
---------------------------|
#.#|#.#|#.#|#.#|#.#|#.#|#.#|
..#|#..|..#|#..|..#|#.#|..#|
###|#.#|#.#|#.#|#.#|#.#|###|
---------------------------|
#.#|#.#|#.#|###|#.#|###|###|
#.#|..#|#.#|...|...|..#|..#|
#.#|###|#.#|#.#|###|#.#|#.#|
---------------------------|
###|#.#|###|#.#|###|###|###|
#..|..#|#..|#.#|...|..#|...|
#.#|###|#.#|#.#|#.#|#.#|###|
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
