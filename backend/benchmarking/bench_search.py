import timeit
from server.model.search import Optimizer
from server.model.factories import create_maze
from server.model.game import Board, BoardLocation, MazeCard, Piece



def test_optimizer_d0_direct_path():
    _benchmark_optimizer(create_maze(MAZE_STRING), MazeCard.create_instance(
        "NE", 0), BoardLocation(6, 2), BoardLocation(3, 3))


def test_optimizer_d0_shift_required():
    _benchmark_optimizer(create_maze(MAZE_STRING), MazeCard.create_instance(
        "NE", 0), BoardLocation(0, 3), BoardLocation(3, 3))

def test_optimizer_d1():
    _benchmark_optimizer(create_maze(MAZE_STRING), MazeCard.create_instance(
        "NE", 0), BoardLocation(6, 6), BoardLocation(3, 3))


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

def _benchmark_optimizer(maze, leftover_card, objective_location, start_location):
    optimizer = _setup(maze, leftover_card, objective_location, start_location)
    repeat = 5
    runs = 1
    print("Best of 5: {:2f}ms".format(min(timeit.Timer(optimizer.find_optimal_move).repeat(repeat, runs)) / runs * 1000))

def _setup(maze, leftover_card, objective_location, start_location):
    maze = create_maze(MAZE_STRING)
    board = Board(maze=maze, leftover_card=leftover_card, objective_maze_card=maze[objective_location])
    board.clear_pieces()
    piece = Piece(board.maze[start_location])
    board.pieces.append(piece)
    optimizer = Optimizer(board, piece)
    return optimizer