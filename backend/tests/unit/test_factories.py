""" Tests for module model.factories """
import math
from collections import Counter
from server.model.factories import create_maze_and_leftover, create_maze
from server.model.game import BoardLocation, MazeCard



def test_create_maze_and_leftover_fixed_pieces_for_size_7():
    """ Tests create_maze_and_leftover.
    Checks corners and fixed t-juncts. """
    maze, _ = create_maze_and_leftover()
    _assert_corners(maze)
    _assert_fixed_pieces_t_juncts(maze)

def test_create_maze_and_leftover_fixed_pieces_for_size_9():
    """ Tests create_maze_and_leftover.
    Checks corners, fixed t-juncts, and cross center. """
    maze, _ = create_maze_and_leftover(size=9)
    _assert_corners(maze)
    _assert_fixed_pieces_t_juncts(maze)
    _assert_cross_center(maze)
    
def test_create_maze_and_leftover_no_cross_for_size_11():
    """ Tests create_maze_and_leftover.
    Checks that there is no cross maze card for size 11, because it is not of the form 4k + 1. """
    maze, leftover = create_maze_and_leftover()
    assert leftover.doors != MazeCard.CROSS
    for location in maze.maze_locations:
        assert maze[location].doors != MazeCard.CROSS

def test_create_maze_and_leftover_unique_ids_for_size_7():
    """ Tests create_maze_and_leftover.
    Checks unique ids. """
    maze, leftover = create_maze_and_leftover()
    ids = _assert_unique_ids(maze)
    assert leftover.identifier not in ids

def test_create_maze_and_leftover_distribution_for_size_7():
    """ Tests create_maze_and_leftover.
    Checks maze card type distribution. """
    maze, leftover = create_maze_and_leftover()
    doors = [maze[location].doors for location in maze.maze_locations]
    doors.append(leftover.doors)
    assert len(doors) == 50
    counts = Counter(doors)
    assert counts[MazeCard.CORNER] == 19
    assert counts[MazeCard.T_JUNCT] == 18
    assert counts[MazeCard.STRAIGHT] == 13

def test_diagonal_locations_for_size_7():
    """ Checks that the maze cards on the diagonals are rotated
    such that the cards on the center-to-NE look like a T (T_JUNCT rotated by 90), 
    and the clockwise subsequent ones are successively rotated by 90 degrees. """
    maze, _ = create_maze_and_leftover()
    assert maze[BoardLocation(2, 4)].rotation == 90
    assert maze[BoardLocation(4, 4)].rotation == 180
    assert maze[BoardLocation(4, 2)].rotation == 270
    assert maze[BoardLocation(2, 2)].rotation == 0

def test_diagonal_locations_for_size_13():
    """ Same as above, but for size 13. Only checks one location per sector """
    maze, _ = create_maze_and_leftover(size=13)
    assert maze[BoardLocation(4, 8)].rotation == 90
    assert maze[BoardLocation(8, 8)].rotation == 180
    assert maze[BoardLocation(8, 4)].rotation == 270
    assert maze[BoardLocation(4, 4)].rotation == 0

def test_create_maze_and_leftover_distribution_for_size_13():
    """ Tests create_maze_and_leftover.
    Checks maze card type distribution for non-fixed cards in a maze of size 13.
    The distribution should by approximately equal to the
    non-fixed distribution of the original game, i.e. (15, 6, 13) for corners, t-juncts, and straights. """
    size = 13
    maze, leftover = create_maze_and_leftover(size=size)
    doors = [maze[location].doors for location in maze.maze_locations]
    doors.append(leftover.doors)
    assert len(doors) == 170
    non_fixed = len(doors) - 49
    counts = Counter(doors)
    assert counts[MazeCard.CROSS] == 1
    approx_expected_corners = math.floor(15 / 34 * non_fixed + 4)
    approx_expected_t_juncts = math.floor(6 / 34 * non_fixed + 44)
    approx_expected_straights = math.floor(13 / 34 * non_fixed)
    assert approx_expected_corners <= counts[MazeCard.CORNER] <= approx_expected_corners + 1
    assert approx_expected_t_juncts <= counts[MazeCard.T_JUNCT] <= approx_expected_t_juncts + 1
    assert approx_expected_straights <= counts[MazeCard.STRAIGHT] <= approx_expected_straights + 1

maze_string_3 = """
#.#|###|#.#|
#..|..#|...|
#.#|#.#|###|
------------
###|#.#|#.#|
...|...|#.#|
#.#|#.#|#.#|
------------
#.#|#.#|###|
#..|..#|...|
###|###|###|
-----------*
"""

def test_create_fixed_maze_for_size_3():
    """ Creates a fixed maze of size 3 using a maze string.
    Checks every single position for correct layout. """
    maze = create_maze(maze_string_3)
    assert maze.maze_size == 3
    assert maze[BoardLocation(0, 0)].doors == MazeCard.T_JUNCT
    assert maze[BoardLocation(0, 0)].rotation == 0
    assert maze[BoardLocation(0, 1)].doors == MazeCard.CORNER
    assert maze[BoardLocation(0, 1)].rotation == 180
    assert maze[BoardLocation(0, 2)].doors == MazeCard.T_JUNCT
    assert maze[BoardLocation(0, 2)].rotation == 270
    assert maze[BoardLocation(1, 0)].doors == MazeCard.T_JUNCT
    assert maze[BoardLocation(1, 0)].rotation == 90
    assert maze[BoardLocation(1, 1)].doors == MazeCard.CROSS
    assert maze[BoardLocation(1, 2)].doors == MazeCard.STRAIGHT
    assert maze[BoardLocation(1, 2)].rotation == 0
    assert maze[BoardLocation(2, 0)].doors == MazeCard.CORNER
    assert maze[BoardLocation(2, 0)].rotation == 0
    assert maze[BoardLocation(2, 1)].doors == MazeCard.CORNER
    assert maze[BoardLocation(2, 1)].rotation == 270
    assert maze[BoardLocation(2, 2)].doors == MazeCard.STRAIGHT
    assert maze[BoardLocation(2, 2)].rotation == 90


def _assert_unique_ids(maze):
    ids = set()
    for row in range(maze.maze_size):
        for column in range(maze.maze_size):
            current_id = maze[BoardLocation(row, column)].identifier
            assert current_id not in ids
            ids.add(current_id)
    return ids


def _assert_corners(maze):
    border = maze.maze_size - 1
    assert maze[BoardLocation(0, 0)].doors == MazeCard.CORNER
    assert maze[BoardLocation(0, 0)].rotation == 90
    assert maze[BoardLocation(0, border)].doors == MazeCard.CORNER
    assert maze[BoardLocation(0, border)].rotation == 180
    assert maze[BoardLocation(border, border)].doors == MazeCard.CORNER
    assert maze[BoardLocation(border, border)].rotation == 270
    assert maze[BoardLocation(border, 0)].doors == MazeCard.CORNER
    assert maze[BoardLocation(border, 0)].rotation == 0


def _assert_fixed_pieces_t_juncts(maze):
    border = maze.maze_size - 1
    expected_t_junct_locations = [BoardLocation(row, column) for row in range(0, maze.maze_size, 2) for column in range(0, maze.maze_size, 2)]
    expected_t_junct_locations.remove(BoardLocation(0, 0))
    expected_t_junct_locations.remove(BoardLocation(0, border))
    expected_t_junct_locations.remove(BoardLocation(border, border))
    expected_t_junct_locations.remove(BoardLocation(border, 0))
    if border % 4 == 0:
        expected_t_junct_locations.remove(BoardLocation(border // 2, border // 2))
    for location in expected_t_junct_locations:
        assert maze[location].doors == MazeCard.T_JUNCT

def _assert_cross_center(maze):
    center = (maze.maze_size - 1) // 2
    center_location = BoardLocation(center, center)
    assert maze[center_location].doors == MazeCard.CROSS
