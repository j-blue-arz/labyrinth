""" Tests for module computer in model. The classes contained in this are multithreaded.
The tests only run these classes in a single thread, by calling run() directly. """
import copy
from unittest.mock import Mock, patch, PropertyMock

import labyrinth.model.factories as factory
from labyrinth.model.computer import ComputerPlayer
from labyrinth.model.game import Board, BoardLocation, Game, Turns


def test_computer_player__when_register_in_turns__calls_add_player_on_turns_with_callback():
    """ Tests that register_in_turns calls method in turns with callback """
    turns = Mock()
    player = ComputerPlayer(library_binding_factory=Mock(), shift_url="shift-url",
                            move_url="move-url", identifier=9)
    player.register_in_turns(turns)

    turns.add_player.assert_called_once()
    assert turns.add_player.call_args[0][0] == player
    assert turns.add_player.call_args[1]["turn_callback"] is not None


@patch('time.sleep', return_value=None)
@patch.object(ComputerPlayer, "_post_shift")
@patch.object(ComputerPlayer, "_post_move")
def given_library_binding__when_computer_player_run__calls_start_on_binding(post_move, post_shift,
                                                                            time_sleep):
    """ Tests that the computer player calls start() one its computation method.
    """
    game = factory.create_game(with_delay=False)
    library_factory, library = _mock_library_binding()
    player = ComputerPlayer(library_binding_factory=library_factory, move_url="move-url", shift_url="shift-url",
                            identifier=9)
    player.set_game(game)
    player.run()

    library.start.assert_called_once()


@patch('time.sleep', return_value=None)
@patch.object(ComputerPlayer, "_post_shift")
@patch.object(ComputerPlayer, "_post_move")
def given_library_binding__when_library_finished__calls_post_shift_but_not_post_move(post_move,
                                                                                     post_shift,
                                                                                     time_sleep):
    game = factory.create_game(game_id=7, with_delay=False)
    library_factory, library = _mock_library_binding()
    player = ComputerPlayer(library_binding_factory=library_factory, move_url="move-url", shift_url="shift-url",
                            identifier=9)
    player.set_game(game)
    player.run()

    post_shift.assert_called_once_with(BoardLocation(0, 1), 90)
    post_move.assert_called_once_with(BoardLocation(0, 0))


def _mock_library_binding():
    mock_computation_method = Mock()
    mock_computation_method.start = Mock()
    mock_computation_method.shift_action = BoardLocation(0, 1), 90
    mock_computation_method.move_action = BoardLocation(0, 0)
    mock_computation_method_factory = Mock()
    mock_computation_method_factory.return_value = mock_computation_method
    return mock_computation_method_factory, mock_computation_method


def test_random_actions_computes_valid_actions():
    """ Runs computation 100 times and expects that it returns valid actions in each run """
    orig_board = create_board()
    for _ in range(100):
        board = copy.deepcopy(orig_board)
        game = Game(0, board=board, turns=Turns())
        computer_player = ComputerPlayer(library_binding_factory=Mock(), move_url="move-url", shift_url="shift-url",
                                         identifier=9)
        computer_player.set_game(game)
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
    board = create_board()
    piece = board.create_piece()
    piece.maze_card = board.maze[BoardLocation(3, 6)]
    game = Game(0, board=board, turns=Turns())
    computer_player = ComputerPlayer(library_binding_factory=Mock(), move_url="move-url", shift_url="shift-url",
                                     identifier=9, piece=piece)
    computer_player.set_game(game)

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
    orig_board = create_board()
    for _ in range(50):
        board = copy.deepcopy(orig_board)
        maze = board.maze
        piece = board.create_piece()
        piece.maze_card = maze[BoardLocation(0, 0)]
        game = Game(0, board=board, turns=Turns())
        game.previous_shift_location = BoardLocation(0, 3)
        computer_player = ComputerPlayer(library_binding_factory=Mock(), move_url="move-url", shift_url="shift-url",
                                         identifier=9, piece=piece)
        computer_player.set_game(game)
        shift_action, _ = computer_player.random_actions()
        shift_location, _ = shift_action
        assert shift_location != BoardLocation(6, 3)


def create_board():
    card_factory = factory.MazeCardFactory()
    maze = factory.create_maze(MAZE_STRING, card_factory)
    leftover = card_factory.create_instance("NE", 0)
    return Board(maze=maze, leftover_card=leftover)
    

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
