""" Tests for exhaustive search algorithm.
Each testcase verifies the precomputed depth of the found solution,
and asserts that the solution is valid """
import pytest
import copy
from server.model.search import Optimizer
from server.model.factories import create_maze
from server.model.game import Board, BoardLocation, MazeCard, Piece


def test_d1_direct_path():
    """ Test-case where there is a direct path from start location to objective in the initial state """
    params = _param_tuple_to_params(*CASES_PARAMS["d1-direct-path"])
    optimizer = _setup(**params)
    actions = optimizer.find_optimal_move_succession()
    board, piece = _create_board_and_piece(**params)
    assert len(actions) == 2
    _check_actions(board, piece, actions)


def test_d1_shift_req():
    """ Test-case where one shift action is required to reach objective """
    params = _param_tuple_to_params(*CASES_PARAMS["d1-shift-req"])
    optimizer = _setup(**params)
    actions = optimizer.find_optimal_move_succession()
    board, piece = _create_board_and_piece(**params)
    assert len(actions) == 2
    _check_actions(board, piece, actions)


def test_d2_two_shifts():
    """ Test-case where two shift actions are required to reach objective """
    params = _param_tuple_to_params(*CASES_PARAMS["d2-two-shifts"])
    optimizer = _setup(**params)
    actions = optimizer.find_optimal_move_succession()
    board, piece = _create_board_and_piece(**params)
    assert len(actions) == 4
    _check_actions(board, piece, actions)


def test_d2_self_push_out():
    """ Test-case where solution is to push himself out, two turns required """
    params = _param_tuple_to_params(*CASES_PARAMS["d2-self-push-out"])
    optimizer = _setup(**params)
    actions = optimizer.find_optimal_move_succession()
    board, piece = _create_board_and_piece(**params)
    assert len(actions) == 4
    _check_actions(board, piece, actions)


@pytest.mark.skip("long running-time")
def test_d2_long_running():
    """ Long running test-case (ca. 30s), two turns required """
    params = _param_tuple_to_params(*CASES_PARAMS["d2-long-running"])
    optimizer = _setup(**params)
    actions = optimizer.find_optimal_move_succession()
    board, piece = _create_board_and_piece(**params)
    assert len(actions) == 4
    _check_actions(board, piece, actions)


def test_d3_obj_push_out():
    """ Test-case where solution is to push objective out, three turns required """
    params = _param_tuple_to_params(*CASES_PARAMS["d3-obj-push-out"])
    optimizer = _setup(**params)
    actions = optimizer.find_optimal_move_succession()
    board, piece = _create_board_and_piece(**params)
    assert len(actions) == 6
    _check_actions(board, piece, actions)


@pytest.mark.skip("long running-time")
def test_d3_long_running():
    """ Long running test-case (ca. 100s), three turns required """
    params = _param_tuple_to_params(*CASES_PARAMS["d3-long-running"])
    optimizer = _setup(**params)
    actions = optimizer.find_optimal_move_succession()
    board, piece = _create_board_and_piece(**params)
    assert len(actions) == 6
    _check_actions(board, piece, actions)


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

DIFFICULT_MAZE_STRING = """
###|#.#|###|###|#.#|###|###|
#..|#..|...|#..|#..|#..|..#|
#.#|###|#.#|#.#|###|#.#|#.#|
---------------------------|
#.#|#.#|#.#|###|#.#|#.#|###|
#..|..#|..#|...|#..|#.#|...|
###|###|#.#|###|###|#.#|###|
---------------------------|
#.#|###|#.#|#.#|###|###|#.#|
#..|#..|#..|#.#|...|...|..#|
#.#|#.#|#.#|#.#|#.#|###|#.#|
---------------------------|
###|#.#|###|#.#|###|###|###|
...|..#|#..|#.#|#..|...|...|
###|#.#|#.#|#.#|#.#|###|###|
---------------------------|
#.#|#.#|#.#|#.#|#.#|###|#.#|
#..|#..|#..|#.#|..#|...|...|
#.#|###|#.#|#.#|#.#|###|###|
---------------------------|
###|#.#|#.#|#.#|#.#|#.#|#.#|
..#|#..|#..|...|#.#|#..|..#|
#.#|###|#.#|###|#.#|#.#|#.#|
---------------------------|
#.#|###|###|###|#.#|#.#|#.#|
#..|...|#..|...|#.#|...|..#|
###|###|#.#|###|#.#|###|###|
---------------------------*

"""


def _setup(maze, leftover_card, start_location, objective_location):
    board = Board(maze=maze, leftover_card=leftover_card, objective_maze_card=maze[objective_location])
    board.clear_pieces()
    piece = Piece(board.maze[start_location])
    board.pieces.append(piece)
    optimizer = Optimizer(board, piece)
    return optimizer


CASES_PARAMS = {
    "d1-direct-path": (MAZE_STRING, "NE", 0, (3, 3), (6, 2)),
    "d1-shift-req": (MAZE_STRING, "NE", 0, (3, 3), (0, 3)),
    "d2-two-shifts": (MAZE_STRING, "NE", 0, (3, 3), (6, 6)),
    "d2-self-push-out": (DIFFICULT_MAZE_STRING, "NE", 0, (0, 6), (6, 6)),
    "d2-long-running": (MAZE_STRING, "NES", 270, (3, 2), (0, 5)),
    "d3-obj-push-out": (DIFFICULT_MAZE_STRING, "NE", 0, (0, 6), (5, 1)),
    "d3-long-running": (DIFFICULT_MAZE_STRING, "NS", 180, (4, 6), (1, 1))
}


def _param_tuple_to_params(maze_string, leftover_doors, leftover_rotation, start_tuple, objective_tuple):
    return {"maze": create_maze(maze_string),
            "leftover_card": MazeCard.create_instance(leftover_doors, leftover_rotation),
            "start_location": BoardLocation(*start_tuple),
            "objective_location": BoardLocation(*objective_tuple)}


def _create_board_and_piece(maze, leftover_card, objective_location, start_location):
    maze = copy.deepcopy(maze)
    board = Board(maze=maze, leftover_card=leftover_card, objective_maze_card=maze[objective_location])
    board.clear_pieces()
    piece = Piece(board.maze[start_location])
    board.pieces.append(piece)
    return board, piece


def _setup(maze, leftover_card, objective_location, start_location):
    board, piece = _create_board_and_piece(maze, leftover_card, objective_location, start_location)
    optimizer = Optimizer(board, piece)
    return optimizer

def _check_actions(board, piece, actions):
    assert len(actions) % 2 == 0
    reached = False
    for (shift_action, move_location) in zip(actions[0::2], actions[1::2]):
        board.shift(shift_action[0], shift_action[1])
        reached = board.move(piece, move_location)
    assert reached
