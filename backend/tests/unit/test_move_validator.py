""" Tests for MoveValidator. A Board instance is created from a string representation of a labyrinth.
Several validation tests are performed on this instance """

from domain.model import BoardLocation
from domain.validation import MoveValidator
from maze_factory import create_maze


def test_validate_move_for_same_location():
    """ Tests validate_move """
    maze = create_maze(MAZE_STRING)
    validator = MoveValidator(maze)
    assert validator.validate_move(BoardLocation(0, 0), BoardLocation(0, 0))


def test_validate_move_for_unconnected_neighbors():
    """ Tests validate_move """
    maze = create_maze(MAZE_STRING)
    validator = MoveValidator(maze)
    assert not validator.validate_move(BoardLocation(0, 0), BoardLocation(1, 0))
    assert not validator.validate_move(BoardLocation(0, 0), BoardLocation(0, 1))
    assert not validator.validate_move(BoardLocation(2, 4), BoardLocation(2, 5))


def test_validate_move_for_connected_neighbors():
    """ Tests validate_move """
    maze = create_maze(MAZE_STRING)
    validator = MoveValidator(maze)
    assert validator.validate_move(BoardLocation(2, 4), BoardLocation(1, 4))
    assert validator.validate_move(BoardLocation(2, 4), BoardLocation(2, 3))
    assert validator.validate_move(BoardLocation(2, 4), BoardLocation(3, 4))


def test_validate_move_for_connected_neighbors_wo_direct_path():
    """ Tests validate_move """
    maze = create_maze(MAZE_STRING)
    validator = MoveValidator(maze)
    assert validator.validate_move(BoardLocation(3, 1), BoardLocation(3, 2))


def test_validate_move_for_connected_distant_cards():
    """ Tests validate_move """
    maze = create_maze(MAZE_STRING)
    validator = MoveValidator(maze)
    assert validator.validate_move(BoardLocation(1, 4), BoardLocation(5, 0))


def test_validate_move_for_unconnected_cards_with_only_one_wall():
    """ Tests validate_move """
    maze = create_maze(MAZE_STRING)
    validator = MoveValidator(maze)
    assert not validator.validate_move(BoardLocation(1, 0), BoardLocation(4, 4))


def test_validate_move_for_paths_on_border():
    """ Tests validate_move """
    maze = create_maze(MAZE_STRING)
    validator = MoveValidator(maze)
    assert validator.validate_move(BoardLocation(5, 0), BoardLocation(6, 3))
    assert validator.validate_move(BoardLocation(0, 6), BoardLocation(2, 6))


def test_validate_move_for_swapped_locations():
    """ Tests validate_move """
    maze = create_maze(MAZE_STRING)
    validator = MoveValidator(maze)
    assert not validator.validate_move(BoardLocation(1, 0), BoardLocation(0, 0))
    assert not validator.validate_move(BoardLocation(0, 1), BoardLocation(0, 0))
    assert not validator.validate_move(BoardLocation(2, 5), BoardLocation(2, 4))

    assert validator.validate_move(BoardLocation(1, 4), BoardLocation(2, 4))
    assert validator.validate_move(BoardLocation(2, 3), BoardLocation(2, 4))
    assert validator.validate_move(BoardLocation(3, 4), BoardLocation(2, 4))

    assert validator.validate_move(BoardLocation(3, 2), BoardLocation(3, 1))

    assert validator.validate_move(BoardLocation(5, 0), BoardLocation(1, 4))

    assert not validator.validate_move(BoardLocation(4, 4), BoardLocation(1, 0))

    assert validator.validate_move(BoardLocation(6, 3), BoardLocation(5, 0))
    assert validator.validate_move(BoardLocation(2, 6), BoardLocation(0, 6))


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