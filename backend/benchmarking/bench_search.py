""" Usage:
bench_search <task> <case>
where task is either 'profile' or 'benchmark'
and 'case' is one of "d1-direct-path", "d1-shift-req", "d2-two-shifts", "d2-self-push-out", "d3-obj-push-out".
"""
import timeit
import cProfile
import sys
from random import randint
from server.model.search import Optimizer
from server.model.factories import create_maze, create_random_maze_card, create_random_original_maze_and_leftover, \
                                   print_maze
from server.model.game import BoardLocation
import tests.unit.test_optimizer as setup


def _find_setups():
    actions = []
    maze_card = None
    start_location = None
    objective_location = None
    maze = create_maze(setup.GENERATED_WITH_LINE_LEFTOVER)
    while len(actions) <= 6:
        maze_card = create_random_maze_card(doors="NS")
        start_location = BoardLocation(randint(0, 6), randint(0, 6))
        objective_location = BoardLocation(randint(0, 6), randint(0, 6))
        board, piece = setup._create_board_and_piece(maze, maze_card, start_location, objective_location)
        optimizer = Optimizer(board, piece)
        start = timeit.default_timer()
        actions = optimizer.find_optimal_actions()
        stop = timeit.default_timer()
        if len(actions) > 5:
            print("Found setup of depth {}, with actions: {}, running for {:.2f}s".format(
                len(actions) / 2, actions, stop - start))
            print("Setup: {} {} {}".format(maze_card, start_location, objective_location))
    print("Found setup of depth {} with actions: {}".format(len(actions)/2, actions))
    print("Setup: {} {} {}".format(maze_card, start_location, objective_location))

def _generate_and_print_maze_string():
    maze, leftover = create_random_original_maze_and_leftover()
    print_maze(maze)
    print(leftover)



def _benchmark(name):
    repeat = 3
    runs = 1
    optimizer, _, _ = setup.create_optimizer(name)
    min_time = min(timeit.Timer(optimizer.find_optimal_actions).repeat(repeat, runs)) / runs * 1000
    print("Test case {:<17} \t best of {}: {:.2f}ms".format(name, repeat, min_time))


def _profile(name):
    optimizer, _, _ = setup.create_optimizer(name)
    cProfile.runctx("optimizer.find_optimal_actions()", globals(), locals(), filename=name)


def _main(argv):
    mode = "benchmark"
    case_name = "all"
    if len(argv) > 1:
        mode = argv[1]
    if len(argv) > 2:
        case_name = argv[2]
    cases = []
    if case_name == "all":
        cases = setup.CASES_PARAMS.keys()
    else:
        cases = [case_name]
    for name in cases:
        if mode == "benchmark":
            _benchmark(name)
        elif mode == "profile":
            _profile(name)


if __name__ == "__main__":
    _main(sys.argv)
    #_find_setups()
    #_generate_and_print_maze_string()
