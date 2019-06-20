""" Tests for minimax algorithm.
Each testcase verifies the depth of the found solution,
and asserts that the solution is valid.
There are currently four types of test cases:
- d1_shift_req is based on the case in test_exhaustive_search with the same name.
All others are based on d2_long_running.
- d2_cannot_prevent is a case where the algorithm cannot prevent the other player from reaching the objective.
- d3_can_prevent is a case where the algorithm has to prevent the other player
                        from reaching the objective in his first move,
                        but then cannot reach the objective himself in his second.
- d3_reach is a case where the other player is prevented from reaching, and the algorithm reaches in his second move.
These types are implemented on two boards.
"""
import copy
import pytest
import server.model.algorithm.minimax as mm
from tests.unit.factories import param_tuple_to_param_dict, create_board_and_pieces
from server.model.game import Board, BoardLocation, MazeCard, Piece
from tests.unit.mazes import MINIMAX_BIG_COMPONENT_MAZE, MINIMAX_BUG_MAZE, MINIMAX_DIFFICULT_MAZE

def test_big_component_d1_shift_req_with_depth_1():
    """ Test-case where one shift action is required to reach objective.
    Optimizer is run with depth 1.
    Checks that objective was reached. """
    optimizer, board, pieces = create_optimizer("big-component-d1-shift-req", depth=1)
    actions, value = optimizer.find_actions()
    assert value == 1
    was_reached = _check_actions(board, pieces[0], actions)
    assert was_reached

def test_big_component_d1_shift_req_with_depth_2():
    """ Test-case where one shift action is required to reach objective.
    Optimizer is run with depth 2.
    Checks that objective was reached """
    optimizer, board, pieces = create_optimizer("big-component-d1-shift-req", depth=2)
    actions, value = optimizer.find_actions()
    assert value == 1
    was_reached = _check_actions(board, pieces[0], actions)
    assert was_reached

def test_big_component_d2_cannot_prevent():
    """ Test-case where other player reaches objective, check that a valid action was returned """
    optimizer, board, pieces = create_optimizer("big-component-d2-cannot-prevent", depth=2)
    actions, value = optimizer.find_actions()
    assert value == -1
    _check_actions(board, pieces[0], actions)


@pytest.mark.skip("long running-time")
def test_big_component_d3_reach():
    """ Test-case where player reaches objective in his second move, other player cannot prevent this to happen.
    Check specific first actions. """
    optimizer, board, pieces = create_optimizer("big-component-d3-reach", depth=3)
    actions, value = optimizer.find_actions()
    assert value == 1
    _check_actions(board, pieces[0], actions)
    shift_location, shift_rotation = actions[0]
    move_location = actions[1]
    assert (shift_location == BoardLocation(0, 5) and move_location == BoardLocation(6, 5))


def test_difficult_d1_shift_req_with_depth_1():
    """ Test-case where one shift action is required to reach objective.
    Optimizer is run with depth 1.
    Checks that objective was reached """
    optimizer, board, pieces = create_optimizer("difficult-d1-shift-req", depth=1)
    actions, value = optimizer.find_actions()
    assert value == 1
    was_reached = _check_actions(board, pieces[0], actions)
    assert was_reached

def test_difficult_d1_shift_req_with_depth_2():
    """ Test-case where one shift action is required to reach objective.
    Optimizer is run with depth 1.
    Checks that objective was reached """
    optimizer, board, pieces = create_optimizer("difficult-d1-shift-req", depth=2)
    actions, value = optimizer.find_actions()
    assert value == 1
    was_reached = _check_actions(board, pieces[0], actions)
    assert was_reached

def test_difficult_d2_cannot_prevent():
    """ Test-case where other player reaches objective, check that a valid action was returned """
    optimizer, board, pieces = create_optimizer("difficult-d2-cannot-prevent", depth=2)
    actions, value = optimizer.find_actions()
    assert value == -1
    _check_actions(board, pieces[0], actions)

def test_difficult_d2_can_prevent():
    """ Test-case where noone reaches objective,
    check specific player's first action """
    optimizer, board, pieces = create_optimizer("difficult-d2-can-prevent", depth=2)
    actions, value = optimizer.find_actions()
    assert value == 0
    _check_actions(board, pieces[0], actions)
    shift_location, _ = actions[0]
    assert shift_location == BoardLocation(1, 6)

@pytest.mark.skip("long running-time")
def test_difficult_d3_reach():
    """ Test-case where player reaches objective in his second move, other player cannot prevent this to happen.
    Check specific first actions. """
    optimizer, board, pieces = create_optimizer("difficult-d3-reach", depth=3)
    actions, value = optimizer.find_actions()
    assert value == 1
    _check_actions(board, pieces[0], actions)
    shift_location, shift_rotation = actions[0]
    move_location = actions[1]
    assert (shift_location == BoardLocation(0, 3) and move_location == BoardLocation(6, 3)) or \
           (shift_location == BoardLocation(6, 3) and move_location == BoardLocation(4, 2)) or \
           (shift_location == BoardLocation(6, 3) and move_location == BoardLocation(3, 3))

def test_bug_d1_with_depth_1():
    """ Test case which resulted in a bug where the leftover straight was inserted at (6, 3), 0,
    and the algorithm then tried to move to the unconnected objective location (6, 2) """
    optimizer, board, pieces = create_optimizer("bug-d1", depth=1)
    actions, value = optimizer.find_actions()
    assert value == 1
    _check_actions(board, pieces[0], actions)

def test_bug_d1_with_depth_2():
    """ Test case which resulted in a bug where the leftover straight was inserted at (6, 3), 0,
    and the algorithm then tried to move to the unconnected objective location (6, 2) """
    optimizer, board, pieces = create_optimizer("bug-d1", depth=2)
    actions, value = optimizer.find_actions()
    assert value == 1
    _check_actions(board, pieces[0], actions)

CASES_PARAMS = {
    "big-component-d1-shift-req": (MINIMAX_BIG_COMPONENT_MAZE, "NE", [(3, 3), (6, 6)], (0, 3)),
    "big-component-d2-cannot-prevent": (MINIMAX_BIG_COMPONENT_MAZE, "NS", [(3, 2), (0, 4)], (0, 5)),
    "big-component-d3-reach": (MINIMAX_BIG_COMPONENT_MAZE, "NE", [(6, 6), (0, 0)], (0, 6)), #solution: ((0, 5), x), (6, 5)
    "difficult-d1-shift-req": (MINIMAX_DIFFICULT_MAZE, "NE", [(3, 3), (3, 3)], (6, 2)), #solution: ((0, 3), x), (6, 2)
    "difficult-d2-cannot-prevent": (MINIMAX_DIFFICULT_MAZE, "NE", [(3, 3), (0, 0)], (1, 1)),
    "difficult-d2-can-prevent": (MINIMAX_DIFFICULT_MAZE, "NE", [(3, 3), (2, 6)], (0, 6)), #solution: ((1, 6), x)
    "difficult-d3-reach": (MINIMAX_DIFFICULT_MAZE, "NE", [(2, 3), (6, 6)], (0, 2)), # ((0, 3), 270) , (6, 3)
    "bug-d1": (MINIMAX_BUG_MAZE, "NS", [(4, 5), (0, 2)], (6, 2))
}

def create_optimizer(key, previous_shift_location=None, depth=3):
    """Creates a test case, instantiates an Optimizer with this case.

    :param key: a key for the test-case
    :return: an Optimizer instance, the board and the piece of the created test-case
    """
    param_dict = param_tuple_to_param_dict(*(CASES_PARAMS[key]))
    board = create_board_and_pieces(**param_dict)
    optimizer = mm.Minimax(board, board.pieces, previous_shift_location=previous_shift_location, depth=depth)
    return optimizer, board, board.pieces

def _check_actions(board, piece, actions):
    assert len(actions) == 2
    shift_action = actions[0]
    move_location = actions[1]
    board.shift(shift_action[0], shift_action[1])
    return board.move(piece, move_location)