""" Tests for Graph. A Board instance is created from a string representation of a labyrinth.
Several validation tests are performed on this instance """

from model.game import BoardLocation
from model.maze_algorithm import Graph
from model.factories import create_maze

def test_is_reachable_for_same_location():
    """ Tests is_reachable """
    maze = create_maze(MAZE_STRING)
    graph = Graph(maze)
    assert graph.is_reachable(BoardLocation(0, 0), BoardLocation(0, 0))


def test_is_reachable_for_unconnected_neighbors():
    """ Tests is_reachable """
    maze = create_maze(MAZE_STRING)
    graph = Graph(maze)
    assert not graph.is_reachable(BoardLocation(0, 0), BoardLocation(1, 0))
    assert not graph.is_reachable(BoardLocation(0, 0), BoardLocation(0, 1))
    assert not graph.is_reachable(BoardLocation(2, 4), BoardLocation(2, 5))


def test_is_reachable_for_connected_neighbors():
    """ Tests is_reachable """
    maze = create_maze(MAZE_STRING)
    graph = Graph(maze)
    assert graph.is_reachable(BoardLocation(2, 4), BoardLocation(1, 4))
    assert graph.is_reachable(BoardLocation(2, 4), BoardLocation(2, 3))
    assert graph.is_reachable(BoardLocation(2, 4), BoardLocation(3, 4))


def test_is_reachable_for_connected_neighbors_wo_direct_path():
    """ Tests is_reachable """
    maze = create_maze(MAZE_STRING)
    graph = Graph(maze)
    assert graph.is_reachable(BoardLocation(3, 1), BoardLocation(3, 2))


def test_is_reachable_for_connected_distant_cards():
    """ Tests is_reachable """
    maze = create_maze(MAZE_STRING)
    graph = Graph(maze)
    assert graph.is_reachable(BoardLocation(1, 4), BoardLocation(5, 0))


def test_is_reachable_for_unconnected_cards_with_only_one_wall():
    """ Tests is_reachable """
    maze = create_maze(MAZE_STRING)
    graph = Graph(maze)
    assert not graph.is_reachable(BoardLocation(1, 0), BoardLocation(4, 4))


def test_is_reachable_for_paths_on_border():
    """ Tests is_reachable """
    maze = create_maze(MAZE_STRING)
    graph = Graph(maze)
    assert graph.is_reachable(BoardLocation(5, 0), BoardLocation(6, 3))
    assert graph.is_reachable(BoardLocation(0, 6), BoardLocation(2, 6))


def test_is_reachable_for_swapped_locations():
    """ Tests is_reachable. Re-runs all of the above tests with swapped locations. """
    maze = create_maze(MAZE_STRING)
    graph = Graph(maze)
    assert not graph.is_reachable(BoardLocation(1, 0), BoardLocation(0, 0))
    assert not graph.is_reachable(BoardLocation(0, 1), BoardLocation(0, 0))
    assert not graph.is_reachable(BoardLocation(2, 5), BoardLocation(2, 4))

    assert graph.is_reachable(BoardLocation(1, 4), BoardLocation(2, 4))
    assert graph.is_reachable(BoardLocation(2, 3), BoardLocation(2, 4))
    assert graph.is_reachable(BoardLocation(3, 4), BoardLocation(2, 4))

    assert graph.is_reachable(BoardLocation(3, 2), BoardLocation(3, 1))

    assert graph.is_reachable(BoardLocation(5, 0), BoardLocation(1, 4))

    assert not graph.is_reachable(BoardLocation(4, 4), BoardLocation(1, 0))

    assert graph.is_reachable(BoardLocation(6, 3), BoardLocation(5, 0))
    assert graph.is_reachable(BoardLocation(2, 6), BoardLocation(0, 6))

def test_reachable_locations():
    """ Tests reachable_locations """
    maze = create_maze(MAZE_STRING)
    graph = Graph(maze)
    reachable = graph.reachable_locations(BoardLocation(0, 1))
    expected = set(BoardLocation(*coord) for coord in [(0, 1), (0, 2), (0, 3), (1, 3)])
    assert set(reachable) == expected



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