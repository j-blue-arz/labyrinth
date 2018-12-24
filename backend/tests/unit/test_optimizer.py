""" Tests for exhaustive search algorithm.
Each testcase verifies the precomputed depth of the found solution,
and asserts that the solution is valid """
import copy
import pytest
from server.model.search import Optimizer
from server.model.factories import create_maze
from server.model.game import Board, BoardLocation, MazeCard, Piece


def test_d1_direct_path():
    """ Test-case where there is a direct path from start location to objective in the initial state """
    optimizer, board, piece = create_optimizer("d1-direct-path")
    actions = optimizer.find_optimal_actions()
    assert len(actions) == 2
    _check_actions(board, piece, actions)


def test_d1_shift_req():
    """ Test-case where one shift action is required to reach objective """
    optimizer, board, piece = create_optimizer("d1-shift-req")
    actions = optimizer.find_optimal_actions()
    assert len(actions) == 2
    _check_actions(board, piece, actions)


def test_d2_two_shifts():
    """ Test-case where two shift actions are required to reach objective """
    optimizer, board, piece = create_optimizer("d2-two-shifts")
    actions = optimizer.find_optimal_actions()
    assert len(actions) == 4
    _check_actions(board, piece, actions)


def test_d2_self_push_out():
    """ Test-case where solution is to push himself out, two turns required """
    optimizer, board, piece = create_optimizer("d2-self-push-out")
    actions = optimizer.find_optimal_actions()
    assert len(actions) == 4
    _check_actions(board, piece, actions)


@pytest.mark.skip("long running-time")
def test_d2_long_running():
    """ Long running test-case (ca. 30s), two turns required """
    optimizer, board, piece = create_optimizer("d2-long-running")
    actions = optimizer.find_optimal_actions()
    assert len(actions) == 4
    _check_actions(board, piece, actions)


def test_d3_obj_push_out():
    """ Test-case where solution is to push objective out, three turns required """
    optimizer, board, piece = create_optimizer("d3-obj-push-out")
    actions = optimizer.find_optimal_actions()
    assert len(actions) == 6
    _check_actions(board, piece, actions)


@pytest.mark.skip("long running-time")
def test_d3_long_running():
    """ Long running test-case (ca. 100s), three turns required """
    optimizer, board, piece = create_optimizer("d3-long-running")
    actions = optimizer.find_optimal_actions()
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

CASES_PARAMS = {
    "d1-direct-path": (MAZE_STRING, "NE", 0, (3, 3), (6, 2)),
    "d1-shift-req": (MAZE_STRING, "NE", 0, (3, 3), (0, 3)),
    "d2-two-shifts": (MAZE_STRING, "NE", 0, (3, 3), (6, 6)),
    "d2-self-push-out": (DIFFICULT_MAZE_STRING, "NE", 0, (0, 6), (6, 6)),
    "d2-long-running": (MAZE_STRING, "NES", 270, (3, 2), (0, 5)),
    "d3-obj-push-out": (DIFFICULT_MAZE_STRING, "NE", 0, (0, 6), (5, 1)),
    "d3-long-running": (DIFFICULT_MAZE_STRING, "NS", 180, (4, 6), (1, 1))
}


def _param_tuple_to_param_dict(maze_string, leftover_doors, leftover_rotation, start_tuple, objective_tuple):
    return {"maze": create_maze(maze_string),
            "leftover_card": MazeCard.create_instance(leftover_doors, leftover_rotation),
            "start_location": BoardLocation(*start_tuple),
            "objective_location": BoardLocation(*objective_tuple)}


def _create_board_and_piece(maze, leftover_card, start_location, objective_location):
    maze = copy.deepcopy(maze)
    board = Board(maze=maze, leftover_card=leftover_card, objective_maze_card=maze[objective_location])
    board.clear_pieces()
    piece = Piece(board.maze[start_location])
    board.pieces.append(piece)
    return board, piece


def create_optimizer(key):
    """Creates a test case, instantiates an Optimizer with this case.

    :param key: a key for the test-case
    :return: an Optimizer instance, the board and the piece of the created test-case
    """
    param_dict = _param_tuple_to_param_dict(*(CASES_PARAMS[key]))
    board, piece = _create_board_and_piece(**param_dict)
    optimizer = Optimizer(board, piece)
    return optimizer, board, piece

def _check_actions(board, piece, actions):
    assert len(actions) % 2 == 0
    reached = False
    for (shift_action, move_location) in zip(actions[0::2], actions[1::2]):
        board.shift(shift_action[0], shift_action[1])
        reached = board.move(piece, move_location)
    assert reached
