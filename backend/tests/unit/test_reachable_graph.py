""" Tests for Graph. A Board instance is created from a string representation of a labyrinth.
Several validation tests are performed on this instance """
from app.model.game import BoardLocation
from app.model.reachable import Graph
from app.model.factories import create_maze


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
    expected = {BoardLocation(*coord) for coord in [(0, 1), (0, 2), (0, 3), (1, 3)]}
    assert set(reachable) == expected


def test_multi_sources_reachable_locations():
    """ Tests reachable_locations with multiple sources """
    maze = create_maze(MAZE_STRING)
    graph = Graph(maze)
    reachable = graph.reachable_locations(sources=[BoardLocation(6, 4), BoardLocation(6, 5)])
    expected = {BoardLocation(*coord) for coord in [(4, 4), (5, 4), (5, 5), (5, 6), (6, 4), (6, 5), (6, 6)]}
    assert set(reachable) == expected


def test_multi_source_reachable_locations_with_sources():
    """ Tests multi-source reachable_locations with returned sources """
    maze = create_maze(MAZE_STRING)
    graph = Graph(maze)
    sources = [BoardLocation(0, 0), BoardLocation(6, 6), BoardLocation(0, 6)]
    reachable = graph.reachable_locations(sources=sources, with_sources=True)
    assert len(reachable) == 9
    sources_to_locations = {source: {reached.location for reached in reachable if reached.source == source}
                            for source in sources}
    expected = {BoardLocation(*coord) for coord in [(5, 5), (5, 6), (6, 5), (6, 6)]}
    assert sources_to_locations[BoardLocation(6, 6)] == expected
    expected = {BoardLocation(*coord) for coord in [(0, 0)]}
    assert sources_to_locations[BoardLocation(0, 0)] == expected
    expected = {BoardLocation(*coord) for coord in [(0, 6), (1, 5), (1, 6), (2, 6)]}
    assert sources_to_locations[BoardLocation(0, 6)] == expected


def test_two_sources_one_component_reachable_locations_with_sources():
    """ Tests multi-source reachable_locations with returned sources.
    Two sources are in the same connected component """
    maze = create_maze(MAZE_STRING)
    graph = Graph(maze)
    sources = [BoardLocation(0, 2), BoardLocation(0, 3)]
    reachable = graph.reachable_locations(sources=sources, with_sources=True)
    assert len(reachable) == 4
    sources_to_locations = {source: {reached.location for reached in reachable if reached.source == source}
                            for source in sources}
    expected = {BoardLocation(*coord) for coord in [(0, 1), (0, 2)]}
    assert sources_to_locations[BoardLocation(0, 2)] == expected
    expected = {BoardLocation(*coord) for coord in [(0, 3), (1, 3)]}
    assert sources_to_locations[BoardLocation(0, 3)] == expected


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
