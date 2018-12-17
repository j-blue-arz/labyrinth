""" Tests for module model.factories """
from model.factories import create_random_maze
from model.game import BoardLocation, MazeCard


def test_create_random_maze_generates_unique_ids_for_each_maze_card():
    """ Tests create_random_maze """
    maze = create_random_maze()
    ids = set()
    for row in range(maze.MAZE_SIZE):
        for column in range(maze.MAZE_SIZE):
            current_id = maze[BoardLocation(row, column)].identifier
            assert current_id not in ids
            ids.add(current_id)

def test_create_random_maze_fixes_corner_of_board():
    """ Tests create_random_maze """
    maze = create_random_maze()
    extent = maze.MAZE_SIZE - 1
    assert maze[BoardLocation(0, 0)].doors == MazeCard.CORNER
    assert maze[BoardLocation(0, 0)].rotation == 90
    assert maze[BoardLocation(0, extent)].doors == MazeCard.CORNER
    assert maze[BoardLocation(0, extent)].rotation == 180
    assert maze[BoardLocation(extent, extent)].doors == MazeCard.CORNER
    assert maze[BoardLocation(extent, extent)].rotation == 270
    assert maze[BoardLocation(extent, 0)].doors == MazeCard.CORNER
    assert maze[BoardLocation(extent, 0)].rotation == 0
