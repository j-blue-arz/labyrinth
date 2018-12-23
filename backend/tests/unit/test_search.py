from server.model.search import GameTreeNode, Optimizer
from model.factories import create_maze
from model.game import Board, BoardLocation, MazeCard, Piece
from timeit import default_timer as timer


def test_optimizer_d0_direct_path():
    _test_optimizer(create_maze(MAZE_STRING), MazeCard.create_instance(
        "NE", 0), BoardLocation(6, 2), BoardLocation(3, 3), 0)


def test_optimizer_d0_shift_required():
    _test_optimizer(create_maze(MAZE_STRING), MazeCard.create_instance(
        "NE", 0), BoardLocation(0, 3), BoardLocation(3, 3), 0)

def test_optimizer_d1():
    _test_optimizer(create_maze(MAZE_STRING), MazeCard.create_instance(
        "NE", 0), BoardLocation(6, 6), BoardLocation(3, 3), 0)


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


def _test_optimizer(maze, leftover_card, objective_location, start_location, expected_depth):
    maze = create_maze(MAZE_STRING)
    board = Board(maze=maze, leftover_card=leftover_card, objective_maze_card=maze[objective_location])
    board.clear_pieces()
    piece = Piece(board.maze[start_location])
    board.pieces.append(piece)
    optimizer = Optimizer(board, piece)
    shift_action, move_location, depth = optimizer.find_optimal_move()
    assert depth == expected_depth