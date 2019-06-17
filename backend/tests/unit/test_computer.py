""" Tests for module computer in model. The classes contained in this are multithreaded.
The tests only run these classes in a single thread, by calling run() directly. """
import copy
from unittest.mock import MagicMock, patch, PropertyMock
from server.model.computer import ComputerPlayer, RandomActionsAlgorithm
from server.model.factories import create_maze, MazeCardFactory
from server.model.game import Board, MazeCard, BoardLocation, Game


def test_computer_player_fetches_urls_from_url_supplier():
    """ Creates a ComputerPlayer with the url_supplier parameter, and expects
    that the constructor calls methods on the url_supplier """
    url_supplier = MagicMock()
    url_supplier.get_shift_url.return_value = "shift-url"
    url_supplier.get_move_url.return_value = "move-url"
    game = MagicMock()
    type(game).identifier = PropertyMock(return_value=7)
    player = ComputerPlayer(algorithm_name="random", url_supplier=url_supplier, game=game, identifier=9)
    url_supplier.get_shift_url.assert_called_once_with(7, 9)
    url_supplier.get_move_url.assert_called_once_with(7, 9)
    assert player.shift_url == "shift-url"
    assert player.move_url == "move-url"


def test_computer_player_algorithm_name():
    """ Tests that ComputerPlayer constructor chooses algorithm RandomActionsAlgorithm,
    when algorithm_name is 'random' """
    player = ComputerPlayer(algorithm_name="random", shift_url="shift-url",
                            move_url="move-url", game=None, identifier=9)
    assert player.algorithm is RandomActionsAlgorithm


def test_computer_player_register_in_turns():
    """ Tests that register_in_turns calls method in turns with callback """
    turns = MagicMock()
    player = ComputerPlayer(algorithm_name="random", shift_url="shift-url",
                            move_url="move-url", game=None, identifier=9)
    player.register_in_turns(turns)
    turns.add_player.assert_called_once_with(player, turn_callback=player.start)


@patch('time.sleep', return_value=None)
@patch.object(RandomActionsAlgorithm, "start", autospec=True, side_effect=RandomActionsAlgorithm.run)
@patch.object(ComputerPlayer, "_post_shift")
@patch.object(ComputerPlayer, "_post_move")
def test_computer_player_starts_algorithm(post_move, post_shift, algorithm_start, time_sleep):
    """ Tests that the computer player starts algorithm.
    .start() is patched so that the algorithm runs sequentially.
    """
    card_factory = MazeCardFactory()
    board = Board(create_maze(MAZE_STRING, card_factory), leftover_card=card_factory.create_instance("NE", 0))
    piece = board.create_piece()
    game = MagicMock()
    type(game).identifier = PropertyMock(return_value=7)
    game.get_enabled_shift_locations.return_value = board.insert_locations
    player = ComputerPlayer(algorithm_name="random", move_url="move-url", shift_url="shift-url",
                            game=game, identifier=9, board=board, piece=piece)
    player.run()
    algorithm_start.assert_called_once()
    post_shift.assert_called_once()
    post_move.assert_called_once()
    insert_location, rotation = post_shift.call_args[0]
    move_location = post_move.call_args[0][0]
    assert rotation in [0, 90, 180, 270]
    assert insert_location in board.insert_locations
    assert move_location in board.maze.maze_locations


def test_random_actions_algorithm_computes_valid_actions():
    """ Runs algorithm 100 times and expects that it returns valid actions in each run """
    card_factory = MazeCardFactory()
    orig_board = Board(create_maze(MAZE_STRING, card_factory), leftover_card=card_factory.create_instance("NE", 0))
    for _ in range(100):
        board = copy.deepcopy(orig_board)
        maze = board.maze
        piece = board.create_piece()
        piece.maze_card = maze[BoardLocation(0, 0)]
        game = MagicMock()
        game.get_enabled_shift_locations.return_value = board.insert_locations
        algorithm = RandomActionsAlgorithm(board, piece, game)
        assert algorithm.shift_action is None
        assert algorithm.move_action is None
        algorithm.run()
        insert_location, insert_rotation = algorithm.shift_action
        move_location = algorithm.move_action
        assert insert_rotation in [0, 90, 180, 270]
        assert insert_location in board.insert_locations
        allowed_coordinates = [(0, 0)]
        if insert_location == BoardLocation(0, 1) and insert_rotation == 270:
            allowed_coordinates = allowed_coordinates + [(0, 1)]
        elif insert_location == BoardLocation(0, 1) and insert_rotation == 180:
            allowed_coordinates = allowed_coordinates + [(0, 1), (1, 1)]
        elif insert_location == BoardLocation(1, 0) and insert_rotation == 270:
            allowed_coordinates = allowed_coordinates + [(1, 0)]
        elif insert_location == BoardLocation(1, 0) and insert_rotation == 0:
            allowed_coordinates = allowed_coordinates + [(1, 0), (1, 1), (1, 2), (2, 1), (2, 2), (3, 1), (3, 2)]
        elif insert_location == BoardLocation(6, 1):
            allowed_coordinates = allowed_coordinates + [(0, 1), (0, 2), (1, 1), (2, 1)]
        allowed_moves = set(BoardLocation(*coordinates) for coordinates in allowed_coordinates)
        assert move_location in allowed_moves


def test_random_actions_algorithm_should_have_different_results():
    """ Runs algorithm 200 times and checks that a certain move is performed sooner or later.
    This test has a probability of about 0.008 to fail. """
    card_factory = MazeCardFactory()
    orig_board = Board(create_maze(MAZE_STRING, card_factory), leftover_card=card_factory.create_instance("NE", 0))
    move_locations = set()
    for _ in range(200):
        board = copy.deepcopy(orig_board)
        maze = board.maze
        piece = board.create_piece()
        piece.maze_card = maze[BoardLocation(0, 0)]
        game = MagicMock()
        game.get_enabled_shift_locations.return_value = board.insert_locations
        algorithm = RandomActionsAlgorithm(board, piece, game)
        algorithm.run()
        move_locations.add(algorithm.move_action)
    assert BoardLocation(2, 1) in move_locations


@patch('time.sleep', return_value=None)
@patch.object(RandomActionsAlgorithm, "start", autospec=True, side_effect=RandomActionsAlgorithm.run)
@patch.object(ComputerPlayer, "_post_shift")
@patch.object(ComputerPlayer, "_post_move")
def test_computer_player_random_algorith_when_piece_is_pushed_out(post_move, post_shift, algorithm_start, time_sleep):
    """ Tests case where piece is positioned on an insert position, so that it is pushed out.
    Runs algorithm 100 times. Push-out expectation rate is 1/12.
    Probability that no push-out takes place in 100 runs is negligible
    .start() is patched so that the algorithm runs sequentially.
    This test recreates a bug, where the pushed-out piece is not updated correctly, leading
    to exceptions thrown when computer makes a move.
    """
    card_factory = MazeCardFactory()
    board = Board(create_maze(MAZE_STRING, card_factory), leftover_card=card_factory.create_instance("NE", 0))
    piece = board.create_piece()
    piece.maze_card = board.maze[BoardLocation(3, 6)]
    game = MagicMock()
    game.get_enabled_shift_locations.return_value = board.insert_locations
    player = ComputerPlayer(algorithm_name="random", move_url="move-url", shift_url="shift-url",
                            game=game, identifier=9, board=board, piece=piece)
    for _ in range(100):
        player.run()
        insert_location, _ = post_shift.call_args[0]
        move_location = post_move.call_args[0][0]
        allowed_coordinates = [(3, 6)]
        if insert_location == BoardLocation(3, 6):
            allowed_coordinates = [(3, 5)]
        elif insert_location == BoardLocation(3, 0):
            allowed_coordinates = [(3, 0)]
        allowed_moves = set(BoardLocation(*coordinates) for coordinates in allowed_coordinates)
        assert move_location in allowed_moves


def test_random_actions_algorithm_should_respect_no_pushback_rule():
    """ Runs algorithm 50 times and checks that none of the computed shifts reverts the previous shift action """

    card_factory = MazeCardFactory()
    orig_board = Board(create_maze(MAZE_STRING, card_factory), leftover_card=card_factory.create_instance("NE", 0))
    for _ in range(50):
        board = copy.deepcopy(orig_board)
        maze = board.maze
        piece = board.create_piece()
        piece.maze_card = maze[BoardLocation(0, 0)]
        game = Game(0, board=orig_board)
        game.previous_shift_location = BoardLocation(0, 3)
        algorithm = RandomActionsAlgorithm(board, piece, game)
        algorithm.run()
        insert_location, _ = algorithm.shift_action
        assert insert_location != BoardLocation(6, 3)


@patch('time.sleep', return_value=None)
@patch.object(RandomActionsAlgorithm, "start", autospec=True, side_effect=RandomActionsAlgorithm.run)
@patch.object(ComputerPlayer, "_post_shift")
@patch.object(ComputerPlayer, "_post_move")
def test_computer_player_random_algorith_respects_no_pushback_rule(post_move, post_shift, algorithm_start, time_sleep):
    """ Tests case where a previous shift cannot be reversed
    Runs algorithm 100 times. No shift should reverse previous shift.
    .start() is patched so that the algorithm runs sequentially.
    This test recreates a bug, where the algorithm was not informed of the previous shift,
    leading to invalid shift actions.
    """
    card_factory = MazeCardFactory()
    board = Board(create_maze(MAZE_STRING, card_factory), leftover_card=card_factory.create_instance("NE", 0))
    piece = board.create_piece()
    previous_shift_location = BoardLocation(6, 1)
    game = MagicMock()
    game.get_enabled_shift_locations.return_value = board.insert_locations.difference({previous_shift_location})
    type(game).identifier = PropertyMock(return_value=7)
    piece.maze_card = board.maze[BoardLocation(3, 6)]
    player = ComputerPlayer(algorithm_name="random", move_url="move-url", shift_url="shift-url",
                            game=game, identifier=9, board=board, piece=piece)
    for _ in range(100):
        player.run()
        insert_location, _ = post_shift.call_args[0]
        assert insert_location != BoardLocation(6, 1)


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
