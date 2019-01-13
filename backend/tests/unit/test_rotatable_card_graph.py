""" Tests for Graph. A Board instance is created from a string representation of a labyrinth.
Several validation tests are performed on this instance """
from server.model.game import BoardLocation
from server.model.maze_algorithm import RotatableMazeCardGraph
from server.model.factories import create_maze


def test_rotatable_unreached():
    """ Tests reachable_locations where the rotatable is not reached """
    maze = create_maze(MAZE_STRING)
    graph = RotatableMazeCardGraph(maze, BoardLocation(0, 5))
    reachable, reachable_map = graph.reachable_locations(BoardLocation(0, 1))
    expected = {BoardLocation(*coord) for coord in [(0, 1), (0, 2), (0, 3), (1, 3)]}
    assert reachable == expected
    assert reachable_map == dict()


def test_rotatable_dead_end():
    """ Tests reachable_locations where the rotatable is reached, but no paths are leaving """
    maze = create_maze(MAZE_STRING)
    graph = RotatableMazeCardGraph(maze, BoardLocation(0, 5))
    reachable, reachable_map = graph.reachable_locations(BoardLocation(0, 4))
    assert reachable == {BoardLocation(0, 4)}
    assert reachable_map == {180: {BoardLocation(0, 5)}, 270: {BoardLocation(0, 5)}}


def test_start_from_rotatable():
    """ Tests reachable_locations where the rotatable is the start """
    maze = create_maze(MAZE_STRING)
    graph = RotatableMazeCardGraph(maze, BoardLocation(6, 6))
    reachable, reachable_map = graph.reachable_locations(BoardLocation(6, 6))
    assert reachable == dict()
    expected_for_all_rotations_but_90 = {BoardLocation(*coord) for coord in [(6, 6), (5, 6), (6, 5), (5, 5)]}
    for rotation in [0, 180, 270]:
        assert reachable_map[rotation] == expected_for_all_rotations_but_90
    assert reachable_map[90] == {BoardLocation(6, 6)}


def test_rotatable_straight():
    """ Tests reachable_locations where the rotatable is a straight.
    Map is expected to have an entry for two rotations. """
    maze = create_maze(MAZE_STRING)
    graph = RotatableMazeCardGraph(maze, BoardLocation(5, 4))
    reachable, reachable_map = graph.reachable_locations(BoardLocation(6, 4))
    assert reachable == {BoardLocation(6, 4)}
    expected_0_and_180 = {BoardLocation(*coord) for coord in [(5, 4), (4, 4)]}
    assert reachable_map == {0: expected_0_and_180, 180: expected_0_and_180}


def test_rotatable_t_junct_four_subtrees():
    """ Tests reachable_locations where the rotatable is a t-junct
    and each rotation should result in a different result.
    The map is expected to have three different entries. """
    maze = create_maze(MAZE_STRING)
    graph = RotatableMazeCardGraph(maze, BoardLocation(3, 5))
    reachable, reachable_map = graph.reachable_locations(BoardLocation(3, 3))
    assert len(reachable) == 24
    expected_90 = {BoardLocation(*coord) for coord in [(3, 5), (3, 6), (4, 5), (4, 6)]}
    expected_180 = {BoardLocation(*coord) for coord in [(3, 5), (2, 5), (4, 5), (4, 6)]}
    expected_270 = {BoardLocation(*coord) for coord in [(3, 5), (2, 5), (3, 6)]}
    assert reachable_map[90] == expected_90
    assert reachable_map[180] == expected_180
    assert reachable_map[270] == expected_270
    assert 0 not in reachable_map


def test_rotable_reached_from_two_directions():
    """ Tests reachable_locations where the rotatable can be reached from two opposing locations. """
    maze = create_maze(MAZE_STRING)
    graph = RotatableMazeCardGraph(maze, BoardLocation(4, 1))
    reachable, reachable_map = graph.reachable_locations(BoardLocation(3, 1))
    assert len(reachable) == 26
    assert BoardLocation(4, 1) not in reachable
    assert reachable_map == {0: {BoardLocation(4, 2), BoardLocation(4, 1)},
                             90: {BoardLocation(4, 2), BoardLocation(4, 1)},
                             180: {BoardLocation(4, 0), BoardLocation(4, 1)},
                             270: {BoardLocation(4, 0), BoardLocation(4, 1)}}


def test_rotatable_reached_from_three_directions():
    """ Tests reachable_locations where the rotatable is on the border and can be reached from all three locations.
    The rotatable is a straight, so
    it is expected to be in the certainly reachable set, and the map is empty for all rotations. """
    maze = create_maze(MAZE_STRING)
    graph = RotatableMazeCardGraph(maze, BoardLocation(5, 0))
    reachable, reachable_map = graph.reachable_locations(BoardLocation(3, 1))
    assert len(reachable) == 27
    for rotation in [0, 90, 180, 270]:
        assert reachable_map[rotation] == {BoardLocation(5, 0)}


MAZE_STRING = """
###|#.#|#.#|###|#.#|#.#|###|
#..|#..|...|...|#..|..#|..#|
#.#|###|###|#.#|###|###|#.#|
---------------------------|
###|###|#.#|#.#|#.#|###|#.#|
...|...|#.#|#..|#.#|...|..#|
#.#|#.#|#.#|###|#.#|###|#.#|
---------------------------|
#.#|#.#|###|###|#.#|#.#|#.#|
#..|#..|...|...|..#|#.#|..#|
#.#|#.#|#.#|#.#|#.#|#.#|#.#|
---------------------------|
#.#|#.#|#.#|###|#.#|###|###|
..#|..#|#..|...|...|...|..#|
###|#.#|###|#.#|###|#.#|#.#|
---------------------------|
###|#.#|###|#.#|###|#.#|###|
#..|..#|...|#.#|...|#..|...|
#.#|###|###|#.#|#.#|###|###|
---------------------------|
###|#.#|###|#.#|#.#|#.#|#.#|
..#|...|...|...|#.#|#..|..#|
#.#|###|#.#|###|#.#|#.#|#.#|
---------------------------|
#.#|#.#|#.#|###|#.#|#.#|#.#|
#..|...|...|...|#.#|...|..#|
###|###|###|###|#.#|###|###|
---------------------------*

"""
