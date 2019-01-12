""" Usage:
bench_exhaustive_search <task> <case>
where task is either 'profile' or 'benchmark'
and 'case' is one of "d1-direct-path", "d1-shift-req", "d2-two-shifts", "d2-self-push-out", "d3-obj-push-out".
"""
import timeit
import cProfile
import sys
from random import randint
import server.model.minimax as mm
from server.model.factories import create_maze
from server.model.game import BoardLocation
import tests.unit.test_minimax as setup


def _benchmark(name):
    repeat = 1
    runs = 1
    optimizer, _, _ = setup.create_optimizer(name, depth=_extract_depth(name))
    min_time = min(timeit.Timer(optimizer.find_optimal_actions).repeat(repeat, runs)) / runs * 1000
    print("Test case {:<30} \t best of {}: {:.2f}ms".format(name, repeat, min_time))


def _profile(name):
    optimizer, _, _ = setup.create_optimizer(name, depth=_extract_depth(name))
    cProfile.runctx("optimizer.find_optimal_actions()", globals(), locals(), filename=name)

def _results(name):
    optimizer, _, _ = setup.create_optimizer(name, depth=_extract_depth(name))
    print("Test case {:<30} \t resulted in actions {}".format(name, optimizer.find_optimal_actions()))

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
