""" Usage:
bench_exhaustive_search <task> <case>
where task is either 'profile', 'benchmark', or result
and 'case' is either the name of a specific test case, or
'all' for all test cases defined in test_exhaustive_search
"""
import timeit
import cProfile
import sys
from random import randint
import labyrinth.model.algorithm.exhaustive_search as exh
from labyrinth.model.factories import create_maze_and_leftover, \
    maze_to_string
from labyrinth.model.game import BoardLocation
from tests.unit.mazes import EXH_DEPTH_4_MAZE
from tests.unit.test_exhaustive_search import CASES_PARAMS
import tests.unit.factories as setup


def _find_setups():
    actions = []
    leftover_card = None
    start_location = None
    objective_location = None
    size = 9
    max_index = size - 1
    # card_factory = MazeCardFactory()
    # maze = create_maze(setup.GENERATED_WITH_LINE_LEFTOVER, card_factory)
    while len(actions) <= 8:
        maze, leftover_card = create_maze_and_leftover(size=size)
        start_location = BoardLocation(randint(0, max_index), randint(0, max_index))
        objective_location = BoardLocation(randint(0, max_index), randint(0, max_index))
        board = setup.create_board_and_pieces(maze, leftover_card, start_location, objective_location)
        piece = board.pieces[0]
        optimizer = exh.Optimizer(board, piece)
        start = timeit.default_timer()
        actions = optimizer.find_optimal_actions()
        stop = timeit.default_timer()
        print("Found setup of depth {}, with actions: {}, running for {:.2f}s".format(
            len(actions) // 2, [start_location] + [objective_location] + actions, stop - start))
        if len(actions) > 7:
            print("Setup: {} {} {}".format(leftover_card, start_location, objective_location))
            print("Maze:")
            print(maze_to_string(maze))


def _generate_and_print_maze_string():
    maze, leftover = create_maze_and_leftover()
    print(maze_to_string(maze))
    print(leftover)


BENCH_CASES_PARAMS = {
    "d4-generated-86s": (EXH_DEPTH_4_MAZE, "NE", [(4, 2)], (6, 7))
}


def create_optimizer(key, previous_shift_location=None):
    """Creates a test case, instantiates an Optimizer with this case.

    :param key: a key for the test-case
    :return: an Optimizer instance, the board and the piece of the created test-case
    """
    if key in BENCH_CASES_PARAMS:
        param_dict = setup.param_tuple_to_param_dict(*(BENCH_CASES_PARAMS[key]))
    else:
        param_dict = setup.param_tuple_to_param_dict(*(CASES_PARAMS[key]))
    board = setup.create_board_and_pieces(**param_dict)
    piece = board.pieces[0]
    optimizer = exh.Optimizer(board, piece, previous_shift_location=previous_shift_location)
    return optimizer, board, piece


def _benchmark(name):
    repeat = 3
    runs = 1
    optimizer, _, _ = create_optimizer(name)
    min_time = min(timeit.Timer(optimizer.find_optimal_actions).repeat(repeat, runs)) / runs * 1000
    print("Test case {:<24} \t best of {}: {:.2f}ms".format(name, repeat, min_time))


def _profile(name):
    optimizer, _, _ = create_optimizer(name)
    cProfile.runctx("optimizer.find_optimal_actions()", globals(), locals(), filename=name)


def _results(name):
    optimizer, _, _ = create_optimizer(name)
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
        elif mode == "profile":
            _profile(name)
        elif mode == "result":
            _results(name)


if __name__ == "__main__":
    _main(sys.argv)
    # _find_setups()
    # _generate_and_print_maze_string()
