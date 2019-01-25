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
import server.model.algorithm.alpha_beta as ab
from server.model.factories import create_maze
from server.model.game import Board, BoardLocation, MazeCard, Piece
from tests.unit.mazes import MINIMAX_BIG_COMPONENT_MAZE, MINIMAX_DIFFICULT_MAZE, GENERATED_WITH_LINE_LEFTOVER

def test_big_component_d1_shift_req_with_depth_1():
    """ Test-case where one shift action is required to reach objective.
    Optimizer is run with depth 1.
    Checks that objective was reached. """
    optimizer, board, pieces = create_optimizer("big-component-d1-shift-req", depth=1)
    actions, _, values = optimizer.find_actions()
    assert values[0] == 1
    was_reached = _check_actions(board, pieces[0], actions)
    assert was_reached

def test_big_component_d1_shift_req_with_depth_2():
    """ Test-case where one shift action is required to reach objective.
    Optimizer is run with depth 2.
    Checks that objective was reached """
    optimizer, board, pieces = create_optimizer("big-component-d1-shift-req", depth=2)
    actions, _, values = optimizer.find_actions()
    assert values[0] == 1
    was_reached = _check_actions(board, pieces[0], actions)
    assert was_reached

def test_big_component_d2_cannot_prevent():
    """ Test-case where other player reaches objective, check that a valid action was returned """
    optimizer, board, pieces = create_optimizer("big-component-d2-cannot-prevent", depth=2)
    actions, _, values = optimizer.find_actions()
    assert values[0] == -1
    _check_actions(board, pieces[0], actions)


@pytest.mark.skip("long running-time")
def test_big_component_d3_reach():
    """ Test-case where player reaches objective in his second move, other player cannot prevent this to happen.
    Check specific first actions. """
    optimizer, board, pieces = create_optimizer("big-component-d3-reach", depth=3)
    actions, _, _ = optimizer.find_actions()
    _check_actions(board, pieces[0], actions)


def test_difficult_d1_shift_req_with_depth_1():
    """ Test-case where one shift action is required to reach objective.
    Optimizer is run with depth 1.
    Checks that objective was reached """
    optimizer, board, pieces = create_optimizer("difficult-d1-shift-req", depth=1)
    actions, _, values = optimizer.find_actions()
    assert values[0] == 1
    was_reached = _check_actions(board, pieces[0], actions)
    assert was_reached

def test_difficult_d1_shift_req_with_depth_2():
    """ Test-case where one shift action is required to reach objective.
    Optimizer is run with depth 1.
    Checks that objective was reached """
    optimizer, board, pieces = create_optimizer("difficult-d1-shift-req", depth=2)
    actions, _, values = optimizer.find_actions()
    assert values[0] == 1
    was_reached = _check_actions(board, pieces[0], actions)
    assert was_reached

def test_difficult_d2_cannot_prevent():
    """ Test-case where other player reaches objective, check that a valid action was returned """
    optimizer, board, pieces = create_optimizer("difficult-d2-cannot-prevent", depth=2)
    actions, _, values = optimizer.find_actions()
    assert values[0] == -1
    _check_actions(board, pieces[0], actions)

def test_difficult_d2_can_prevent():
    """ Test-case where noone reaches objective,
    check specific player's first action """
    optimizer, board, pieces = create_optimizer("difficult-d2-can-prevent", depth=2)
    actions, _, _ = optimizer.find_actions()
    _check_actions(board, pieces[0], actions)

@pytest.mark.skip("long running-time")
def test_difficult_d3_reach():
    """ Test-case where player reaches objective in his second move, other player cannot prevent this to happen.
    Check specific first actions. """
    optimizer, board, pieces = create_optimizer("difficult-d3-reach", depth=3)
    actions, _, _ = optimizer.find_actions()
    _check_actions(board, pieces[0], actions)

CASES_PARAMS = {
    "big-component-d1-shift-req": (MINIMAX_BIG_COMPONENT_MAZE, "NE", [(3, 3), (6, 6)], (0, 3)),
    "big-component-d2-cannot-prevent": (MINIMAX_BIG_COMPONENT_MAZE, "NS", [(3, 2), (0, 4)], (0, 5)),
    "big-component-d3-reach": (MINIMAX_BIG_COMPONENT_MAZE, "NE", [(6, 6), (0, 0)], (0, 6)), #solution: ((0, 5), x), (6, 5)
    "difficult-d1-shift-req": (MINIMAX_DIFFICULT_MAZE, "NE", [(3, 3), (3, 3)], (6, 2)), #solution: ((0, 3), x), (6, 2)
    "difficult-d2-cannot-prevent": (MINIMAX_DIFFICULT_MAZE, "NE", [(3, 3), (0, 0)], (1, 1)),
    "difficult-d2-can-prevent": (MINIMAX_DIFFICULT_MAZE, "NE", [(3, 3), (2, 6)], (0, 6)), #solution: ((1, 6), x)
    "difficult-d3-reach": (MINIMAX_DIFFICULT_MAZE, "NE", [(2, 3), (6, 6)], (0, 2)), # ((0, 3), , (6, 3)
    "generated-2-d2": (GENERATED_WITH_LINE_LEFTOVER, "NS", [(1, 4), (1, 4)], (6, 2)),
    "generated-2-d3": (GENERATED_WITH_LINE_LEFTOVER, "NS", [(1, 4), (1, 4)], (6, 2)),
    "generated-5-d2": (GENERATED_WITH_LINE_LEFTOVER, "NS", [(6, 6), (6, 6)], (0, 0)),
    "generated-5-d3": (GENERATED_WITH_LINE_LEFTOVER, "NS", [(6, 6), (6, 6)], (0, 0)),
    "generated-6-d2": (GENERATED_WITH_LINE_LEFTOVER, "NS", [(1, 4), (1, 4)], (5, 6)),
    "generated-6-d3": (GENERATED_WITH_LINE_LEFTOVER, "NS", [(1, 4), (1, 4)], (5, 6)),
    "generated-7-d2": (GENERATED_WITH_LINE_LEFTOVER, "NS", [(6, 2), (6, 6)], (1, 4)),
    "generated-8-d2": (GENERATED_WITH_LINE_LEFTOVER, "NS", [(0, 6), (0, 0)], (6, 6)),
    "big-component-0-d2": (MINIMAX_BIG_COMPONENT_MAZE, "NE", [(6, 6), (0, 0)], (0, 6)),
    "difficult-0-d2": (MINIMAX_DIFFICULT_MAZE, "NE", [(2, 3), (6, 6)], (0, 2)),
}

def _param_tuple_to_param_dict(maze_string, leftover_doors, piece_starts, objective_tuple):
    return {"maze": create_maze(maze_string),
            "leftover_card": MazeCard.create_instance(leftover_doors, 0),
            "piece_locations": [BoardLocation(*piece_start) for piece_start in piece_starts],
            "objective_location": BoardLocation(*objective_tuple)}


def _create_board_and_piece(maze, leftover_card, piece_locations, objective_location):
    maze = copy.deepcopy(maze)
    board = Board(maze=maze, leftover_card=leftover_card, objective_maze_card=maze[objective_location])
    board.clear_pieces()
    for location in piece_locations:
        piece = Piece(board.maze[location])
        board.pieces.append(piece)
    return board


def create_optimizer(key, previous_shift_location=None, depth=3):
    """Creates a test case, instantiates an Optimizer with this case.

    :param key: a key for the test-case
    :return: an Optimizer instance, the board and the piece of the created test-case
    """
    param_dict = _param_tuple_to_param_dict(*(CASES_PARAMS[key]))
    board = _create_board_and_piece(**param_dict)
    optimizer = ab.Minimax(board, board.pieces, previous_shift_location=previous_shift_location, depth=depth)
    return optimizer, board, board.pieces

def _check_actions(board, piece, actions):
    assert len(actions) == 2
    shift_action = actions[0]
    move_location = actions[1]
    board.shift(shift_action[0], shift_action[1])
    return board.move(piece, move_location)