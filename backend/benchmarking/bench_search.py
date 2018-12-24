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
from server.model.factories import create_maze, create_random_maze_card
from server.model.game import Board, BoardLocation, MazeCard, Piece


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
#..|...|...|...|#.#|...|..#|
###|###|#.#|###|#.#|###|###|
---------------------------*

"""

DIFFICULT_MAZE_STRING = """
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


def _find_setups():
    actions = []
    maze_card = None
    start_location = None
    objective_location = None
    maze = create_maze(MAZE_STRING)
    while len(actions) <= 6:
        maze_card = create_random_maze_card()
        start_location = BoardLocation(randint(0, 6), randint(0, 6))
        objective_location = BoardLocation(randint(0, 6), randint(0, 6))
        optimizer = _setup(maze, maze_card, start_location, objective_location)
        start = timeit.default_timer()
        actions = optimizer.find_optimal_move_succession()
        stop = timeit.default_timer()
        if (stop - start > 1.0) and len(actions) == 4:
            print("Found setup of depth {}, with actions: {}, running for {:.2f}s".format(len(actions)/2, actions, stop - start))
            print("Setup: {} {} {}".format(maze_card, start_location, objective_location))
    print("Found setup of depth {} with actions: {}".format(len(actions)/2, actions))
    print("Setup: {} {} {}".format(maze_card, start_location, objective_location))


def _benchmark(optimizer, name):
    repeat = 3
    runs = 1
    min_time = min(timeit.Timer(optimizer.find_optimal_move).repeat(repeat, runs)) / runs * 1000
    print("Test case {} \t best of {}: {:.2f}ms".format(name, repeat, min_time))


def _profile(optimizer, name):
    cProfile.runctx("optimizer.find_optimal_move()", globals(), locals(), filename=name)


def _setup(maze, leftover_card, start_location, objective_location):
    board = Board(maze=maze, leftover_card=leftover_card, objective_maze_card=maze[objective_location])
    board.clear_pieces()
    piece = Piece(board.maze[start_location])
    board.pieces.append(piece)
    optimizer = Optimizer(board, piece)
    return optimizer


CASES_MAP = {
"d1-direct-path": lambda: _setup(create_maze(MAZE_STRING), MazeCard.create_instance("NE", 0), BoardLocation(3, 3), BoardLocation(6, 2)),
"d1-shift-req": lambda: _setup(create_maze(MAZE_STRING), MazeCard.create_instance("NE", 0), BoardLocation(3, 3), BoardLocation(0, 3)),
"d2-two-shifts": lambda: _setup(create_maze(MAZE_STRING), MazeCard.create_instance("NE", 0), BoardLocation(3, 3), BoardLocation(6, 6)),
"d2-self-push-out": lambda: _setup(create_maze(DIFFICULT_MAZE_STRING), MazeCard.create_instance("NE", 0), BoardLocation(0, 6), BoardLocation(6, 6)),
"d2-long-running": lambda: _setup(create_maze(MAZE_STRING), MazeCard.create_instance("NES", 270), BoardLocation(3, 2), BoardLocation(0, 5)),
"d3-obj-push-out": lambda: _setup(create_maze(DIFFICULT_MAZE_STRING), MazeCard.create_instance("NE", 0), BoardLocation(0, 6), BoardLocation(5, 1)),
"d3-long-running": lambda: _setup(create_maze(DIFFICULT_MAZE_STRING), MazeCard.create_instance("NS", 180), BoardLocation(4, 6), BoardLocation(1, 1))
}

def _main(argv):
    mode = "benchmark"
    case_name = "all"
    if len(argv) > 1:
        mode = argv[1]
    if len(argv) > 2:
        case_name = argv[2]
    cases = []
    if case_name == "all":
        cases = CASES_MAP.keys()
    else:
        cases = [case_name]
    for name in cases:
        if mode == "benchmark":
            _benchmark(CASES_MAP[name](), name)
        elif mode == "profile":
            _profile(CASES_MAP[name](), name)

if __name__ == "__main__":
    _main(sys.argv)
    #_find_setups()