""" Tests for module computer in model. The classes contained in this are multithreaded.
The tests only run these classes in a single thread, by calling run() directly. """
import copy
from unittest.mock import Mock, patch, PropertyMock

from labyrinth.model.computer import ComputerPlayer
from labyrinth.model.factories import create_maze, MazeCardFactory
from labyrinth.model.game import Board, BoardLocation, Game


def test_computer_player_register_in_turns():
    """ Tests that register_in_turns calls method in turns with callback """
    turns = Mock()
    player = ComputerPlayer(compute_method_factory=Mock(), shift_url="shift-url",
                            move_url="move-url", game=None, identifier=9)
    player.register_in_turns(turns)
    turns.add_player.assert_called_once_with(player, turn_callback=player.start)


@patch('time.sleep', return_value=None)
@patch.object(ComputerPlayer, "_post_shift")
@patch.object(ComputerPlayer, "_post_move")
def test_computer_player_calls_start_on_compute_method(post_move, post_shift, time_sleep):
    """ Tests that the computer player calls start() one its computation method.
    """
    card_factory = MazeCardFactory()
    board = Board(create_maze(MAZE_STRING, card_factory), leftover_card=card_factory.create_instance("NE", 0))
    piece = board.create_piece()
    game = Mock()
    type(game).identifier = PropertyMock(return_value=7)
    game.get_enabled_shift_locations.return_value = board.shift_locations
    mock_method = Mock()
    mock_method.start = Mock()
    mock_method.shift_action = BoardLocation(0, 1), 90
    mock_method.move_action = board.maze.maze_card_location(piece.maze_card)
    mock_method_factory = Mock()
    mock_method_factory.return_value = mock_method
    player = ComputerPlayer(compute_method_factory=mock_method_factory, move_url="move-url", shift_url="shift-url",
                            game=game, identifier=9, board=board, piece=piece)
    player.run()
    mock_method.start.assert_called_once()
    post_shift.assert_called_once()
    post_move.assert_called_once()


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
        game.board = board
        computer_player = ComputerPlayer(compute_method_factory=Mock(), move_url="move-url", shift_url="shift-url",
                                         game=game, identifier=9, board=board, piece=piece)
        shift_action, move_location = computer_player.random_actions()
        shift_location, shift_rotation = shift_action
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


@patch('time.sleep', return_value=None)
@patch.object(ComputerPlayer, "_post_shift")
@patch.object(ComputerPlayer, "_post_move")
def test_computer_player_random_algorith_when_piece_is_pushed_out(post_move, post_shift, time_sleep):
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
    game.board = board
    computer_player = ComputerPlayer(compute_method_factory=Mock(), move_url="move-url", shift_url="shift-url",
                                     game=game, identifier=9, board=board, piece=piece)

    for _ in range(100):
        shift_action, move_location = computer_player.random_actions()
        shift_location, _ = shift_action
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
        computer_player = ComputerPlayer(compute_method_factory=Mock(), move_url="move-url", shift_url="shift-url",
                                         game=game, identifier=9, board=board, piece=piece)
        shift_action, _ = computer_player.random_actions()
        shift_location, _ = shift_action
        assert shift_location != BoardLocation(6, 3)


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
