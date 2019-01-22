""" Usage:
bench_minimax_heuristic <task> <case>
where task is either 'profile' or 'benchmark'
and 'case' is one of "big-component-d1-shift-req", "big-component-d2-cannot-prevent", "big-component-d3-reach",
"difficult-d1-shift-req", "difficult-d2-cannot-prevent", "difficult-d2-can-prevent", "difficult-d3-reach", "bug-d1".
"""
import timeit
import cProfile
import sys
import copy
from server.model.factories import create_maze
from server.model.game import Board, BoardLocation, MazeCard, Piece
import server.model.minimax_heuristic as heuristic
import tests.unit.test_minimax as setup

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
    param_dict = _param_tuple_to_param_dict(*(setup.CASES_PARAMS[key]))
    board = _create_board_and_piece(**param_dict)
    optimizer = heuristic.Minimax(board, board.pieces, previous_shift_location=previous_shift_location, depth=depth)
    return optimizer, board, board.pieces

def _benchmark(name):
    depth = _extract_depth(name)
    repeat = 3
    if depth >= 3:
        repeat = 1
    runs = 1
    optimizer, _, _ = create_optimizer(name, depth=_extract_depth(name))
    min_time = min(timeit.Timer(optimizer.find_actions).repeat(repeat, runs)) / runs * 1000
    print("Test case {:<30} \t best of {}: {:.2f}ms".format(name, repeat, min_time))


def _profile(name):
    optimizer, _, _ = create_optimizer(name, depth=_extract_depth(name))
    cProfile.runctx("optimizer.find_actions()", globals(), locals(), filename=name)

def _results(name):
    optimizer, _, _ = create_optimizer(name, depth=_extract_depth(name))
    actions, value, values = optimizer.find_actions()
    print("Test case {:<30} \t resulted in actions {}, with total value {}".format(name, actions, value))
    format_str = ', '.join(['{:0.2f}']*len(values))
    print(format_str.format(*values))

def _extract_depth(test_case):
    pos = test_case.find("-d") + 2
    return int(test_case[pos])



def _main(argv):
    mode = "benchmark"
    case_name = "all"
    if len(argv) > 1:
        mode = argv[1]
    if len(argv) > 2:
        case_name = argv[2]
    cases = []
    if case_name == "all":
        all_keys = setup.CASES_PARAMS.keys()
        all_keys_lt_3 = [key for key in all_keys if _extract_depth(key) < 3]
        cases = all_keys_lt_3
    else:
        cases = [case_name]
    for name in cases:
        if mode == "benchmark":
            _benchmark(name)
        elif mode == "profile":
            _profile(name)
        elif mode == "result":
            _results(name)


if __name__ == "__main__":
    _main(sys.argv)
