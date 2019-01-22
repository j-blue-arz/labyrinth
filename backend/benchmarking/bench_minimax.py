""" Usage:
bench_minimax <task> <case>
where task is either 'profile' or 'benchmark'
and 'case' is one of "big-component-d1-shift-req", "big-component-d2-cannot-prevent", "big-component-d3-reach",
"difficult-d1-shift-req", "difficult-d2-cannot-prevent", "difficult-d2-can-prevent", "difficult-d3-reach", "bug-d1".
"""
import timeit
import cProfile
import sys
import tests.unit.test_minimax as setup


def _benchmark(name):
    depth=_extract_depth(name)
    repeat = 3
    if depth >= 3:
        repeat = 1
    runs = 1
    optimizer, _, _ = setup.create_optimizer(name, depth=_extract_depth(name))
    min_time = min(timeit.Timer(optimizer.find_actions).repeat(repeat, runs)) / runs * 1000
    print("Test case {:<30} \t best of {}: {:.2f}ms".format(name, repeat, min_time))


def _profile(name):
    optimizer, _, _ = setup.create_optimizer(name, depth=_extract_depth(name))
    cProfile.runctx("optimizer.find_actions()", globals(), locals(), filename=name)

def _results(name):
    optimizer, _, _ = setup.create_optimizer(name, depth=_extract_depth(name))
    print("Test case {:<30} \t resulted in actions {}".format(name, optimizer.find_actions()))

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
    elif case_name == "all!":
        cases = setup.CASES_PARAMS.keys()
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
