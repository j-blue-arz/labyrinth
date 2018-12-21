""" Tests for module computer in model. The classes contained in this are multithreaded.
The tests only run these classes in a single thread, by calling run() directly. """
import copy
from unittest.mock import MagicMock
from server.model.computer import ComputerPlayer, RandomActionsAlgorithm
from model.factories import create_maze
from model.game import Board, MazeCard, BoardLocation


def test_computer_player_fetches_urls_from_url_supplier():
    """ Creates a ComputerPlayer with the url_supplier parameter, and expects
    that the constructor calls methods on the url_supplier """
    url_supplier = MagicMock()
    url_supplier.get_shift_url.return_value = "shift-url"
    url_supplier.get_move_url.return_value = "move-url"
    player = ComputerPlayer(algorithm_name="random", url_supplier=url_supplier, game_identifier=7, identifier=9)
    url_supplier.get_shift_url.assert_called_once_with(7, 9)
    url_supplier.get_move_url.assert_called_once_with(7, 9)
    assert player.shift_url == "shift-url"
    assert player.move_url == "move-url"


def test_computer_player_algorithm_name():
    """ Tests that ComputerPlayer constructor chooses algorithm RandomActionsAlgorithm,
    when algorithm_name is 'random' """
    player = ComputerPlayer(algorithm_name="random", shift_url="shift-url",
                            move_url="move-url", game_identifier=7, identifier=9)
    assert player.algorithm is RandomActionsAlgorithm


def test_computer_player_register_in_turns():
    """ Tests that register_in_turns calls method in turns with callback """
    turns = MagicMock()
    player = ComputerPlayer(algorithm_name="random", shift_url="shift-url",
                            move_url="move-url", game_identifier=7, identifier=9)
    player.register_in_turns(turns)
    turns.add_player.assert_called_once_with(player, turn_callback=player.start)


def test_random_actions_algorithm_computes_valid_actions():
    """ Runs algorithm 100 times and expects that it returns valid actions in each run """
    orig_board = Board(create_maze(MAZE_STRING), leftover_card=MazeCard.create_instance("NE", 0))
    for _ in range(100):
        board = copy.deepcopy(orig_board)
        maze = board.maze
        piece = board.create_piece()
        piece.maze_card = maze[BoardLocation(0, 0)]
        algorithm = RandomActionsAlgorithm(board, piece)
        assert algorithm.shift_action is None
        assert algorithm.move_action is None
        algorithm.run()
        insert_location, insert_rotation = algorithm.shift_action
        move_location = algorithm.move_action
        assert insert_rotation in [0, 90, 180, 270]
        assert insert_location in maze.insert_locations
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
    orig_board = Board(create_maze(MAZE_STRING), leftover_card=MazeCard.create_instance("NE", 0))
    move_locations = set()
    for _ in range(200):
        board = copy.deepcopy(orig_board)
        maze = board.maze
        piece = board.create_piece()
        piece.maze_card = maze[BoardLocation(0, 0)]
        algorithm = RandomActionsAlgorithm(board, piece)
        algorithm.run()
        move_locations.add(algorithm.move_action)
    assert BoardLocation(2, 1) in move_locations




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
#.#|#..|..#|#..|..#|#.#|..#|
#.#|#.#|#.#|#.#|#.#|#.#|#.#|
---------------------------|
#.#|#.#|#.#|###|#.#|###|###|
..#|..#|#.#|...|...|...|..#|
###|###|#.#|#.#|###|#.#|#.#|
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
