""" Tests for Maze of game.py """
from server.model.game import Maze, MazeCard, BoardLocation
from server.model.factories import create_random_maze, create_random_maze_card


def _get_id_matrix(maze):
    """ Builds a matrix of the maze card identifiers of the given maze """
    id_matrix = [[maze[BoardLocation(row, column)].identifier
                  for column in range(Maze.MAZE_SIZE)]
                 for row in range(Maze.MAZE_SIZE)]
    return id_matrix

def _compare_id_matrices(id_matrix_1, id_matrix_2):
    """ Returns all indices (x, y) where id_matrix_1[x][y] != id_matrix_2[x][y] """
    result = []
    for row in range(Maze.MAZE_SIZE):
        for column in range(Maze.MAZE_SIZE):
            if id_matrix_1[row][column] != id_matrix_2[row][column]:
                result.append((row, column))
    return result

def test_getter_returns_set_card():
    """ Tests setter and getter """
    maze = Maze()
    maze_card = MazeCard()
    maze[BoardLocation(1, 1)] = maze_card
    assert maze[BoardLocation(1, 1)] == maze_card

def test_setter_does_not_alter_other_state():
    """ Tests setter and getter """
    maze = create_random_maze()
    old_id_matrix = _get_id_matrix(maze)
    maze[BoardLocation(3, 3)] = create_random_maze_card()
    new_id_matrix = _get_id_matrix(maze)
    difference = _compare_id_matrices(old_id_matrix, new_id_matrix)
    assert len(difference) == 1
    assert difference[0] == (3, 3)


def test_shift_inserts_leftover():
    """ Tests shift """
    maze = create_random_maze()
    insertion = create_random_maze_card()
    maze.shift(BoardLocation(0, 1), insertion)
    assert maze[BoardLocation(0, 1)] == insertion

def test_shift_returns_pushed_out_card():
    """ Test shift """
    maze = create_random_maze()
    opposite = maze[BoardLocation(0, 3)]
    pushed_out = maze.shift(BoardLocation(Maze.MAZE_SIZE - 1, 3), create_random_maze_card())
    assert opposite == pushed_out


def test_shift_alters_entire_row_correctly():
    """ Test shift """
    maze = create_random_maze()
    old_id_matrix = _get_id_matrix(maze)
    insertion = create_random_maze_card()
    maze.shift(BoardLocation(5, Maze.MAZE_SIZE - 1), insertion)
    new_id_matrix = _get_id_matrix(maze)
    assert new_id_matrix[5][Maze.MAZE_SIZE - 1] == insertion.identifier
    for col in range(Maze.MAZE_SIZE - 1):
        assert new_id_matrix[5][col] == old_id_matrix[5][col + 1]

def test_shift_does_not_alter_rest_of_maze():
    """ Test shift """
    maze = create_random_maze()
    old_id_matrix = _get_id_matrix(maze)
    maze.shift(BoardLocation(5, 0), create_random_maze_card())
    new_id_matrix = _get_id_matrix(maze)
    differences = _compare_id_matrices(old_id_matrix, new_id_matrix)
    assert len(differences) == Maze.MAZE_SIZE
    for difference in differences:
        assert difference[0] == 5

def test_maze_locations_returns_list_of_correct_size():
    """ Test maze_locations """
    maze_locations = [location for location in Maze.maze_locations()]
    assert len(maze_locations) == Maze.MAZE_SIZE * Maze.MAZE_SIZE

def test_maze_locations_returns_list_of_all_maze_locations():
    """ Test maze_locations """
    maze_locations = [location for location in Maze.maze_locations()]
    for row in range(Maze.MAZE_SIZE):
        for column in range(Maze.MAZE_SIZE):
            assert BoardLocation(row, column) in maze_locations

def test_maze_locations_returns_list_in_ascending_order():
    """ Test maze_locations """
    maze_locations = [location for location in Maze.maze_locations()]
    length = len(maze_locations)
    assert maze_locations[0] == BoardLocation(0, 0)
    for first, second in zip(range(length), range(1, length)):
        first_location = maze_locations[first]
        second_location = maze_locations[second]
        assert (first_location.row < second_location.row) or \
                ((first_location.row == second_location.row) and \
                (first_location.column < second_location.column))

def test_maze_card_location_returns_correct_location_for_all_cards():
    """ Test maze_card_location """
    maze = create_random_maze()
    for location in Maze.maze_locations():
        assert maze.maze_card_location(maze[location]) == location

def test_is_inside_returns_true_for_inside_location():
    """ Test is_inside """
    assert Maze.is_inside(BoardLocation(3, 3))
    assert Maze.is_inside(BoardLocation(1, 5))

def test_is_inside_returns_true_for_border_locations():
    """ Test is_inside """
    assert Maze.is_inside(BoardLocation(Maze.MAZE_SIZE-1, 3))
    assert Maze.is_inside(BoardLocation(4, Maze.MAZE_SIZE-1))

def test_is_inside_returns_true_for_corner_location():
    """ Test is_inside """
    assert Maze.is_inside(BoardLocation(Maze.MAZE_SIZE-1, Maze.MAZE_SIZE-1))
    assert Maze.is_inside(BoardLocation(0, Maze.MAZE_SIZE-1))

def test_is_inside_returns_false_for_outside_locations():
    """ Test is_inside """
    assert not Maze.is_inside(BoardLocation(-1, 4))
    assert not Maze.is_inside(BoardLocation(Maze.MAZE_SIZE, 2))
    assert not Maze.is_inside(BoardLocation(0, 14))
    assert not Maze.is_inside(BoardLocation(14, -14))
