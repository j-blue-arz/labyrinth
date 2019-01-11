""" Tests for module model.factories """
from collections import Counter
from server.model.factories import create_random_maze, create_random_original_maze_and_leftover
from server.model.game import BoardLocation, MazeCard


def test_create_random_maze_generates_unique_ids_for_each_maze_card():
    """ Tests create_random_maze """
    maze = create_random_maze()
    _assert_unique_ids(maze)


def test_create_random_maze_fixes_corner_of_board():
    """ Tests create_random_maze """
    maze = create_random_maze()
    _assert_corners(maze, extent=6)


def test_create_random_original_maze_and_leftover_fixed_pieces():
    """ Tests create_random_original_maze_and_leftover.
    Checks corners and fixed t-juncts. """
    maze, _ = create_random_original_maze_and_leftover()
    _assert_corners(maze, extent=6)
    _assert_fixed_pieces_t_juncts(maze)


def test_create_random_original_maze_and_leftover_unique_ids():
    """ Tests create_random_original_maze_and_leftover.
    Checks unique ids. """
    maze, leftover = create_random_original_maze_and_leftover()
    ids = _assert_unique_ids(maze)
    assert leftover.identifier not in ids


def test_create_random_original_maze_and_leftover_distribution():
    """ Tests create_random_original_maze_and_leftover.
    Checks maze card type distribution """
    maze, leftover = create_random_original_maze_and_leftover()
    doors = [maze[location].doors for location in maze.maze_locations()]
    doors.append(leftover.doors)
    assert len(doors) == 50
    counts = Counter(doors)
    assert counts[MazeCard.CORNER] == 19
    assert counts[MazeCard.T_JUNCT] == 18
    assert counts[MazeCard.STRAIGHT] == 13


def _assert_unique_ids(maze):
    ids = set()
    for row in range(maze.MAZE_SIZE):
        for column in range(maze.MAZE_SIZE):
            current_id = maze[BoardLocation(row, column)].identifier
            assert current_id not in ids
            ids.add(current_id)
    return ids


def _assert_corners(maze, extent):
    assert maze[BoardLocation(0, 0)].doors == MazeCard.CORNER
    assert maze[BoardLocation(0, 0)].rotation == 90
    assert maze[BoardLocation(0, extent)].doors == MazeCard.CORNER
    assert maze[BoardLocation(0, extent)].rotation == 180
    assert maze[BoardLocation(extent, extent)].doors == MazeCard.CORNER
    assert maze[BoardLocation(extent, extent)].rotation == 270
    assert maze[BoardLocation(extent, 0)].doors == MazeCard.CORNER
    assert maze[BoardLocation(extent, 0)].rotation == 0


def _assert_fixed_pieces_t_juncts(maze):
    expected_t_junct_locations = [BoardLocation(row, column) for row in range(0, 7, 2) for column in range(0, 7, 2)]
    expected_t_junct_locations.remove(BoardLocation(0, 0))
    expected_t_junct_locations.remove(BoardLocation(0, 6))
    expected_t_junct_locations.remove(BoardLocation(6, 6))
    expected_t_junct_locations.remove(BoardLocation(6, 0))
    for location in expected_t_junct_locations:
        assert maze[location].doors == MazeCard.T_JUNCT
