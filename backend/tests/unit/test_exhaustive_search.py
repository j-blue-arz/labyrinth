""" Tests for exhaustive search algorithm.
Each testcase verifies the precomputed depth of the found solution,
and asserts that the solution is valid """
import copy
import pytest
from library_binding import CompletePathLibraryBinding
from server.model.algorithm.exhaustive_search import Optimizer
from server.model.factories import create_maze, MazeCardFactory
from server.model.game import Board, BoardLocation, MazeCard, Piece


def test_d1_direct_path(create_optimizer):
    """ Test-case where there is a direct path from start location to objective in the initial state """
    board, piece = create_board_and_piece_by_key("d1-direct-path")
    optimizer = create_optimizer(board, piece)
    actions = optimizer.find_optimal_actions()
    assert len(actions) == 2
    _check_actions(board, piece, actions)


def test_d1_shift_req():
    """ Test-case where one shift action is required to reach objective """
    board, piece = create_board_and_piece_by_key("d1-shift-req")
    optimizer = Optimizer(board, piece)
    actions = optimizer.find_optimal_actions()
    assert len(actions) == 2
    _check_actions(board, piece, actions)


def test_d2_two_shifts():
    """ Test-case where two shift actions are required to reach objective """
    board, piece = create_board_and_piece_by_key("d2-two-shifts")
    optimizer = Optimizer(board, piece)
    actions = optimizer.find_optimal_actions()
    assert len(actions) == 4
    _check_actions(board, piece, actions)


def test_d2_self_push_out():
    """ Test-case where solution is to push himself out, two turns required """
    board, piece = create_board_and_piece_by_key("d2-self-push-out")
    optimizer = Optimizer(board, piece)
    actions = optimizer.find_optimal_actions()
    assert len(actions) == 4
    _check_actions(board, piece, actions)


def test_d2_no_pushback_violation():
    """ Test-case where a solution of depth 2 violates no-pushback-rule:
    [((0, 1), 180), (0, 1), ((6, 1), 90), (6, 0)]
    Checks that optimizer does not violate no-pushback-rule """
    board, piece = create_board_and_piece_by_key("d2-pushback-violation")
    optimizer = Optimizer(board, piece)
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
    board, piece = create_board_and_piece_by_key("d2-two-shifts")
    optimizer = Optimizer(board, piece, previous_shift_location=BoardLocation(6, 1))
    actions = optimizer.find_optimal_actions()
    _check_actions(board, piece, actions)
    first_shift_location = actions[0][0]
    assert first_shift_location != BoardLocation(0, 1)

@pytest.mark.skip("long running-time")
def test_d2_long_running():
    """ Two turns required """
    board, piece = create_board_and_piece_by_key("d2-long-running")
    optimizer = Optimizer(board, piece)
    actions = optimizer.find_optimal_actions()
    assert len(actions) == 4
    _check_actions(board, piece, actions)


def test_d3_obj_push_out():
    """ Test-case where solution is to push objective out, three turns required (ca. 7s)"""
    board, piece = create_board_and_piece_by_key("d3-obj-push-out")
    optimizer = Optimizer(board, piece)
    actions = optimizer.find_optimal_actions()
    assert len(actions) == 6
    _check_actions(board, piece, actions)


def test_d3_long_running():
    """ Three turns required """
    board, piece = create_board_and_piece_by_key("d3-long-running")
    optimizer = Optimizer(board, piece)
    actions = optimizer.find_optimal_actions()
    assert len(actions) == 6
    _check_actions(board, piece, actions)

@pytest.mark.skip("long running-time")
def test_d3_generated_1():
    """ three turns required """
    board, piece = create_board_and_piece_by_key("d3-generated-8s")
    optimizer = Optimizer(board, piece)
    actions = optimizer.find_optimal_actions()
    assert len(actions) == 6
    _check_actions(board, piece, actions)

@pytest.mark.skip("long running-time")
def test_d3_generated_2():
    """ three turns required """
    board, piece = create_board_and_piece_by_key("d3-generated-23s")
    optimizer = Optimizer(board, piece)
    actions = optimizer.find_optimal_actions()
    assert len(actions) == 6
    _check_actions(board, piece, actions)

@pytest.mark.skip("long running-time")
def test_d3_generated_3():
    """ three turns required, running-time currently 8s """
    board, piece = create_board_and_piece_by_key("d3-generated-33s")
    optimizer = Optimizer(board, piece)
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
    maze_card_factory = MazeCardFactory()
    return {"maze": create_maze(maze_string, maze_card_factory),
            "leftover_card": maze_card_factory.create_instance(leftover_doors, 0),
            "start_location": BoardLocation(*start_tuple),
            "objective_location": BoardLocation(*objective_tuple)}


def _create_board_and_piece(maze, leftover_card, start_location, objective_location):
    maze = copy.deepcopy(maze)
    board = Board(maze=maze, leftover_card=leftover_card, objective_maze_card=maze[objective_location])
    board.clear_pieces()
    piece = Piece(0, board.maze[start_location])
    board.pieces.append(piece)
    return board, piece

def create_board_and_piece_by_key(key):
    """ Creates a board with a single piece, as used by the exhaustive search optimizer.

    :param key: a key for the test-case
    :return: an Optimizer instance, the board and the piece of the created test-case
    """
    param_dict = _param_tuple_to_param_dict(*(CASES_PARAMS[key]))
    return _create_board_and_piece(**param_dict)

def _check_actions(board, piece, actions):
    assert len(actions) % 2 == 0
    reached = False
    for (shift_action, move_location) in zip(actions[0::2], actions[1::2]):
        board.shift(shift_action[0], shift_action[1])
        reached = board.move(piece, move_location)
    assert reached

@pytest.fixture(params=[Optimizer, CompletePathLibraryBinding])
def create_optimizer(request):

    def _create_optimizer(board, piece, previous_shift_location=None):
        if request.param is Optimizer:
            return Optimizer(board, piece, previous_shift_location)
        if request.param is CompletePathLibraryBinding:
            return CompletePathLibraryBinding("../../lib/libexhsearch.dll", board, piece, previous_shift_location)

    return _create_optimizer
