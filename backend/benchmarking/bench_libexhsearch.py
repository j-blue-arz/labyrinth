""" Usage:
bench_libexhsearch <task> <case>
where task is either 'profile' or 'result'
and 'case' is either the name of a specific test case, or
'all' for all test cases defined in test_exhaustive_search
"""
import timeit
import sys
from tests.unit.mazes import EXH_DEPTH_4_MAZE
from tests.unit.test_exhaustive_search import CASES_PARAMS
import app.model.algorithm.external_library as libexhsearch
from tests.unit.library_binding import CompletePathLibraryBinding
import tests.unit.factories as setup

BENCH_CASES_PARAMS = {
    "d4-generated-86s": (EXH_DEPTH_4_MAZE, "NE", [(4, 2)], (6, 7))
}


def _create_board(key):
    if key in BENCH_CASES_PARAMS:
        param_dict = setup.param_tuple_to_param_dict(*(BENCH_CASES_PARAMS[key]))
    else:
        param_dict = setup.param_tuple_to_param_dict(*(CASES_PARAMS[key]))
    board = setup.create_board_and_pieces(**param_dict)
    return board, board.pieces[0]


def _create_single_result_optimizer(key, previous_shift_location=None):
    """Creates a test case, instantiates an Optimizer with this case.

    :param key: a key for the test-case
    :return: an Optimizer instance, the board and the piece of the created test-case
    """
    board, piece = _create_board(key)
    optimizer = libexhsearch.ExternalLibraryBinding("./lib/libexhsearch.so",
                                                    board, piece, previous_shift_location=previous_shift_location)
    return optimizer, board, piece


def _create_complete_path_optimizer(key, previous_shift_location=None):
    """Creates a test case, instantiates an Optimizer with this case.

    :param key: a key for the test-case
    :return: an Optimizer instance, the board and the piece of the created test-case
    """
    board, piece = _create_board(key)
    optimizer = CompletePathLibraryBinding("./lib/libexhsearch.dll",
                                           board, piece, previous_shift_location=previous_shift_location)
    return optimizer, board, piece


def _benchmark(name):
    repeat = 5
    runs = 1
    optimizer, _, _ = _create_single_result_optimizer(name)
    min_time = min(timeit.Timer(optimizer.find_optimal_action).repeat(repeat, runs)) / runs * 1000
    print("Test case {:<24} \t best of {}: {:.2f}ms".format(name, repeat, min_time))


def _results(name):
    optimizer, _, _ = _create_complete_path_optimizer(name)
    print("Test case {:<24} \t resulted in actions {}".format(name, optimizer.find_optimal_actions()))


def _main(argv):
    mode = "benchmark"
    case_name = "all"
    if len(argv) > 1:
        mode = argv[1]
    if len(argv) > 2:
        case_name = argv[2]
    cases = []
    if case_name == "all":
        cases = CASES_PARAMS.keys()
    else:
        cases = [case_name]
    for name in cases:
        if mode == "benchmark":
            _benchmark(name)
        elif mode == "result":
            _results(name)


if __name__ == "__main__":
    _main(sys.argv)
