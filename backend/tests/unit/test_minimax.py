""" Tests for minimax algorithm.
Each testcase verifies the depth of the found solution,
and asserts that the solution is valid.
There are currently four test cases:
- d1_shift_req is based on the case in test_exhaustive_search with the same name.
All others are based on d2_long_running.
- d2_cannot_prevent is a case where the algorithm cannot prevent the other player from reaching the objective.
- d3_can_prevent is a case where the algorithm has to prevent the other player
                        from reaching the objective in his first move,
                        but then cannot reach the objective himself in his second.
- d3_reach is a case where the other player is prevented from reaching, and the algorithm reaches in his second move. 
"""
import copy
import server.model.minimax as minmax
from server.model.factories import create_maze
from server.model.game import Board, BoardLocation, MazeCard, Piece

def test_d1_shift_req_with_depth_1():
    """ Test-case where one shift action is required to reach objective.
    Optimizer is run with depth 1.
    Checks that objective was reached. """
    optimizer, board, piece = create_optimizer("d1-shift-req", depth=1)
    actions, value = optimizer.find_optimal_actions()
    assert value == 1
    was_reached = _check_actions(board, piece, actions)
    assert was_reached

def test_d1_shift_req_with_depth_2():
    """ Test-case where one shift action is required to reach objective.
    Optimizer is run with depth 2.
    Checks that objective was reached """
    optimizer, board, piece = create_optimizer("d1-shift-req", depth=2)
    actions, value = optimizer.find_optimal_actions()
    assert value == 1
    was_reached = _check_actions(board, piece, actions)
    assert was_reached


def test_d2_cannot_prevent():
    """ Test-case where other player reaches objective, check that a valid action was returned """
    optimizer, board, piece = create_optimizer("d2-cannot-prevent")
    actions, value = optimizer.find_optimal_actions()
    assert value == -1
    _check_actions(board, piece, actions)

def test_d2_can_prevent():
    """ Test-case where noone reaches objective,
    check specific player's first action """
    optimizer, board, piece = create_optimizer("d2-can-prevent")
    actions, value = optimizer.find_optimal_actions()
    assert value == 0
    _check_actions(board, piece, actions)
    shift_location, _ = actions[0]
    assert shift_location == BoardLocation(5, 6)

def test_d3_reach():
    """ Test-case where player reaches objective in his second move, other player cannot prevent this to happen.
    Check specific first actions. """
    optimizer, board, piece = create_optimizer("d3-reach")
    actions, value = optimizer.find_optimal_actions()
    assert value == 1
    _check_actions(board, piece, actions)
    shift_location, shift_rotation = actions[0]
    move_location = actions[1]
    assert shift_location == BoardLocation(0, 5)
    assert shift_rotation == 90
    assert move_location == BoardLocation(3, 0)

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
#..|...|...|...|#.#|#..|..#|
###|###|#.#|###|#.#|###|###|
---------------------------*

"""

CASES_PARAMS = {
    "d1-shift-req": (MAZE_STRING, "NE", (3, 3), (6, 6), (0, 3)),
    "d2-cannot-prevent": (MAZE_STRING, "NS", (3, 2), (0, 4), (0, 5)),
    "d2-can-prevent": (MAZE_STRING, "NES", (3, 2), (4, 5), (5, 6)), #only(?) solution: ((5, 6), x), (y, z) 
    "d3-reach": (MAZE_STRING, "NE", (3, 2), (0, 4), (0, 5)) #only(?) solution: ((0, 5), 90), (3, 0)
}


def _param_tuple_to_param_dict(maze_string, leftover_doors, p1_start, p2_start, objective_tuple):
    return {"maze": create_maze(maze_string),
            "leftover_card": MazeCard.create_instance(leftover_doors, 0),
            "p1_start": BoardLocation(*p1_start),
            "p2_start": BoardLocation(*p2_start),
            "objective_location": BoardLocation(*objective_tuple)}


def _create_board_and_piece(maze, leftover_card, p1_start, p2_start, objective_location):
    maze = copy.deepcopy(maze)
    board = Board(maze=maze, leftover_card=leftover_card, objective_maze_card=maze[objective_location])
    board.clear_pieces()
    piece1 = Piece(board.maze[p1_start])
    piece2 = Piece(board.maze[p2_start])
    board.pieces.append(piece1)
    board.pieces.append(piece2)
    return board, [piece1, piece2]


def create_optimizer(key, previous_shift_location=None, depth=3):
    """Creates a test case, instantiates an Optimizer with this case.

    :param key: a key for the test-case
    :return: an Optimizer instance, the board and the piece of the created test-case
    """
    param_dict = _param_tuple_to_param_dict(*(CASES_PARAMS[key]))
    board, pieces = _create_board_and_piece(**param_dict)
    optimizer = minmax.Optimizer(board, pieces, previous_shift_location=previous_shift_location, depth=depth)
    return optimizer, board, pieces[0]

def _check_actions(board, piece, actions):
    assert len(actions) == 2
    shift_action = actions[0]
    move_location = actions[1]
    board.shift(shift_action[0], shift_action[1])
    return board.move(piece, move_location)
