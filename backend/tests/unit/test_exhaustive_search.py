""" Tests for exhaustive search algorithm.
Each testcase verifies the precomputed depth of the found solution,
and asserts that the solution is valid """
import copy
import pytest
from server.model.algorithm.exhaustive_search import Optimizer
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


def test_d2_no_pushback_violation():
    """ Test-case where a solution of depth 2 violates no-pushback-rule:
    [((0, 1), 180), (0, 1), ((6, 1), 90), (6, 0)]
    Checks that optimizer does not violate no-pushback-rule """
    optimizer, board, piece = create_optimizer("d2-pushback-violation")
    actions = optimizer.find_optimal_actions()
    assert len(actions) == 4
    _check_actions(board, piece, actions)
    for prev_shift_action, shift_action in zip(actions[::2], actions[2::2]):
        prev_shift_location = prev_shift_action[0]
        shift_location = shift_action[0]
        assert board.opposing_insert_location(shift_location) != prev_shift_location

def test_d2_two_shifts_with_previous_shift():
    """ Test case where there is a solution of depth 2: [((0, 1), 0), (4, 5), ((0, 5), 0), (6, 6)]
    The test makes the first shift of this solution a rule violation, and checks
    that the optimizer does not violate no-pushback-rule """
    optimizer, board, piece = create_optimizer("d2-two-shifts", previous_shift_location=BoardLocation(6, 1))
    actions = optimizer.find_optimal_actions()
    _check_actions(board, piece, actions)
    first_shift_location = actions[0][0]
    assert first_shift_location != BoardLocation(0, 1)

@pytest.mark.skip("long running-time")
def test_d2_long_running():
    """ Two turns required """
    optimizer, board, piece = create_optimizer("d2-long-running")
    actions = optimizer.find_optimal_actions()
    assert len(actions) == 4
    _check_actions(board, piece, actions)


def test_d3_obj_push_out():
    """ Test-case where solution is to push objective out, three turns required (ca. 7s)"""
    optimizer, board, piece = create_optimizer("d3-obj-push-out")
    actions = optimizer.find_optimal_actions()
    assert len(actions) == 6
    _check_actions(board, piece, actions)


def test_d3_long_running():
    """ Three turns required """
    optimizer, board, piece = create_optimizer("d3-long-running")
    actions = optimizer.find_optimal_actions()
    assert len(actions) == 6
    _check_actions(board, piece, actions)

@pytest.mark.skip("long running-time")
def test_d3_generated_1():
    """ three turns required """
    optimizer, board, piece = create_optimizer("d3-generated-8s")
    actions = optimizer.find_optimal_actions()
    assert len(actions) == 6
    _check_actions(board, piece, actions)

@pytest.mark.skip("long running-time")
def test_d3_generated_2():
    """ three turns required """
    optimizer, board, piece = create_optimizer("d3-generated-23s")
    actions = optimizer.find_optimal_actions()
    assert len(actions) == 6
    _check_actions(board, piece, actions)

@pytest.mark.skip("long running-time")
def test_d3_generated_3():
    """ three turns required, running-time currently 8s """
    optimizer, board, piece = create_optimizer("d3-generated-33s")
    actions = optimizer.find_optimal_actions()
    assert len(actions) == 6
    _check_actions(board, piece, actions)


BIG_COMPONENT_MAZE = """
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

DIFFICULT_MAZE = """
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

GENERATED_WITH_LINE_LEFTOVER = """
###|#.#|###|#.#|###|###|###|
#..|#.#|...|..#|...|...|..#|
#.#|#.#|#.#|###|#.#|###|#.#|
---------------------------|
###|###|#.#|#.#|###|###|###|
..#|...|#.#|..#|..#|...|#..|
#.#|###|#.#|#.#|#.#|#.#|#.#|
---------------------------|
#.#|###|#.#|#.#|###|###|#.#|
#..|...|#..|#.#|...|...|..#|
#.#|###|#.#|#.#|#.#|###|#.#|
---------------------------|
#.#|###|#.#|#.#|###|#.#|###|
#..|..#|#..|#..|...|#.#|...|
#.#|#.#|###|###|#.#|#.#|###|
---------------------------|
#.#|###|#.#|###|#.#|###|#.#|
#..|..#|...|..#|..#|..#|..#|
#.#|#.#|###|#.#|#.#|#.#|#.#|
---------------------------|
#.#|#.#|###|#.#|###|###|###|
#..|#..|..#|#.#|..#|...|...|
#.#|###|#.#|#.#|#.#|###|###|
---------------------------|
#.#|###|#.#|#.#|#.#|#.#|#.#|
#..|..#|...|#..|...|#..|..#|
###|#.#|###|###|###|#.#|###|
---------------------------*
"""

CASES_PARAMS = {
    "d1-direct-path": (BIG_COMPONENT_MAZE, "NE", (3, 3), (6, 2)),
    "d1-shift-req": (BIG_COMPONENT_MAZE, "NE", (3, 3), (0, 3)),
    "d2-two-shifts": (BIG_COMPONENT_MAZE, "NE", (3, 3), (6, 6)),
    "d2-self-push-out": (DIFFICULT_MAZE, "NE", (0, 6), (6, 6)),
    "d2-pushback-violation": (DIFFICULT_MAZE, "NE", (0, 0), (6, 0)),
    "d2-long-running": (BIG_COMPONENT_MAZE, "NES", (3, 2), (0, 5)),
    "d3-obj-push-out": (DIFFICULT_MAZE, "NE", (0, 6), (5, 1)),
    "d3-long-running": (DIFFICULT_MAZE, "NS", (4, 6), (1, 1)),
    "d3-generated-8s": (GENERATED_WITH_LINE_LEFTOVER, "NS", (1, 4), (6, 2)),
    "d3-generated-23s": (GENERATED_WITH_LINE_LEFTOVER, "NS", (6, 6), (0, 0)),
    "d3-generated-33s": (GENERATED_WITH_LINE_LEFTOVER, "NS", (1, 4), (5, 6))
}


def _param_tuple_to_param_dict(maze_string, leftover_doors, start_tuple, objective_tuple):
    return {"maze": create_maze(maze_string),
            "leftover_card": MazeCard.create_instance(leftover_doors, 0),
            "start_location": BoardLocation(*start_tuple),
            "objective_location": BoardLocation(*objective_tuple)}


def _create_board_and_piece(maze, leftover_card, start_location, objective_location):
    maze = copy.deepcopy(maze)
    board = Board(maze=maze, leftover_card=leftover_card, objective_maze_card=maze[objective_location])
    board.clear_pieces()
    piece = Piece(0, board.maze[start_location])
    board.pieces.append(piece)
    return board, piece


def create_optimizer(key, previous_shift_location=None):
    """Creates a test case, instantiates an Optimizer with this case.

    :param key: a key for the test-case
    :return: an Optimizer instance, the board and the piece of the created test-case
    """
    param_dict = _param_tuple_to_param_dict(*(CASES_PARAMS[key]))
    board, piece = _create_board_and_piece(**param_dict)
    optimizer = Optimizer(board, piece, previous_shift_location=previous_shift_location)
    return optimizer, board, piece

def _check_actions(board, piece, actions):
    assert len(actions) % 2 == 0
    reached = False
    for (shift_action, move_location) in zip(actions[0::2], actions[1::2]):
        board.shift(shift_action[0], shift_action[1])
        reached = board.move(piece, move_location)
    assert reached
    
