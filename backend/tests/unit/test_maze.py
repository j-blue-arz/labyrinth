""" Tests for Maze of game.py """
from server.model.game import Maze, MazeCard, BoardLocation
from tests.unit.factories import create_random_maze, MazeCardFactory


def _get_id_matrix(maze):
    """ Builds a matrix of the maze card identifiers of the given maze """
    id_matrix = [[maze[BoardLocation(row, column)].identifier
                  for column in range(maze.maze_size)]
                 for row in range(maze.maze_size)]
    return id_matrix

def _compare_id_matrices(id_matrix_1, id_matrix_2):
    """ Returns all indices (x, y) where id_matrix_1[x][y] != id_matrix_2[x][y] """
    result = []
    for row in range(len(id_matrix_1)):
        for column in range(len(id_matrix_1[row])):
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
    card_factory = MazeCardFactory()
    maze = create_random_maze(card_factory)
    old_id_matrix = _get_id_matrix(maze)
    maze[BoardLocation(3, 3)] = card_factory.create_random_maze_card()
    new_id_matrix = _get_id_matrix(maze)
    difference = _compare_id_matrices(old_id_matrix, new_id_matrix)
    assert len(difference) == 1
    assert difference[0] == (3, 3)


def test_shift_inserts_leftover():
    """ Tests shift """
    
    card_factory = MazeCardFactory()
    maze = create_random_maze(card_factory)
    insertion = card_factory.create_random_maze_card()
    maze.shift(BoardLocation(0, 1), insertion)
    assert maze[BoardLocation(0, 1)] == insertion

def test_shift_returns_pushed_out_card():
    """ Test shift """
    card_factory = MazeCardFactory()
    maze = create_random_maze(card_factory)
    opposite = maze[BoardLocation(0, 3)]
    pushed_out = maze.shift(BoardLocation(maze.maze_size - 1, 3), card_factory.create_random_maze_card())
    assert opposite == pushed_out


def test_shift_alters_entire_row_correctly():
    """ Test shift """
    card_factory = MazeCardFactory()
    maze = create_random_maze(card_factory)
    old_id_matrix = _get_id_matrix(maze)
    insertion = card_factory.create_random_maze_card()
    maze.shift(BoardLocation(5, maze.maze_size - 1), insertion)
    new_id_matrix = _get_id_matrix(maze)
    assert new_id_matrix[5][maze.maze_size - 1] == insertion.identifier
    for col in range(maze.maze_size - 1):
        assert new_id_matrix[5][col] == old_id_matrix[5][col + 1]

def test_shift_does_not_alter_rest_of_maze():
    """ Test shift """
    card_factory = MazeCardFactory()
    maze = create_random_maze(card_factory)
    old_id_matrix = _get_id_matrix(maze)
    maze.shift(BoardLocation(5, 0), card_factory.create_random_maze_card())
    new_id_matrix = _get_id_matrix(maze)
    differences = _compare_id_matrices(old_id_matrix, new_id_matrix)
    assert len(differences) == maze.maze_size
    for difference in differences:
        assert difference[0] == 5

def test_maze_locations_returns_list_of_correct_size_for_size_7():
    """ Test maze_locations """
    maze = Maze(maze_size=7)
    maze_locations = [location for location in maze.maze_locations]
    assert len(maze_locations) == maze.maze_size * maze.maze_size

def test_maze_locations_returns_list_of_correct_size_for_size_9():
    """ Test maze_locations """
    maze = Maze(maze_size=9)
    maze_locations = [location for location in maze.maze_locations]
    assert len(maze_locations) == maze.maze_size * maze.maze_size

def test_maze_locations_returns_list_of_all_maze_locations_for_size_7():
    """ Test maze_locations """
    maze = Maze(maze_size=7)
    maze_locations = [location for location in maze.maze_locations]
    for row in range(maze.maze_size):
        for column in range(maze.maze_size):
            assert BoardLocation(row, column) in maze_locations

def test_maze_locations_returns_list_of_all_maze_locations_for_size_9():
    """ Test maze_locations """
    maze = Maze(maze_size=9)
    maze_locations = [location for location in maze.maze_locations]
    for row in range(maze.maze_size):
        for column in range(maze.maze_size):
            assert BoardLocation(row, column) in maze_locations

def test_maze_locations_returns_list_in_ascending_order_for_size_7():
    """ Test maze_locations """
    maze = Maze(maze_size=7)
    maze_locations = [location for location in maze.maze_locations]
    _assert_sorted_board_locations(maze_locations)

def test_maze_locations_returns_list_in_ascending_order_for_size_9():
    """ Test maze_locations """
    maze = Maze(maze_size=9)
    maze_locations = [location for location in maze.maze_locations]
    _assert_sorted_board_locations(maze_locations)


def test_maze_card_location_returns_correct_location_for_all_cards():
    """ Test maze_card_location """
    maze = create_random_maze()
    for location in maze.maze_locations:
        assert maze.maze_card_location(maze[location]) == location

def test_is_inside_returns_true_for_inside_location():
    """ Test is_inside """
    maze = Maze(maze_size=7)
    assert maze.is_inside(BoardLocation(3, 3))
    assert maze.is_inside(BoardLocation(1, 5))
    maze = Maze(maze_size=9)
    assert maze.is_inside(BoardLocation(7, 7))
    assert maze.is_inside(BoardLocation(7, 1))

def test_is_inside_returns_true_for_border_locations():
    """ Test is_inside """
    maze = Maze(maze_size=7)
    assert maze.is_inside(BoardLocation(maze.maze_size-1, 3))
    assert maze.is_inside(BoardLocation(4, maze.maze_size-1))
    maze = Maze(maze_size=9)
    assert maze.is_inside(BoardLocation(maze.maze_size-1, 3))
    assert maze.is_inside(BoardLocation(4, maze.maze_size-1))

def test_is_inside_returns_true_for_corner_location():
    """ Test is_inside """
    maze = Maze(maze_size=7)
    assert maze.is_inside(BoardLocation(maze.maze_size-1, maze.maze_size-1))
    assert maze.is_inside(BoardLocation(0, maze.maze_size-1))
    maze = Maze(maze_size=9)
    assert maze.is_inside(BoardLocation(maze.maze_size-1, 3))
    assert maze.is_inside(BoardLocation(4, maze.maze_size-1))

def test_is_inside_returns_false_for_outside_locations():
    """ Test is_inside """
    maze = Maze(maze_size=7)
    assert not maze.is_inside(BoardLocation(-1, 4))
    assert not maze.is_inside(BoardLocation(maze.maze_size, 2))
    assert not maze.is_inside(BoardLocation(0, 14))
    assert not maze.is_inside(BoardLocation(14, -14))
    assert not maze.is_inside(BoardLocation(7, 7))
    maze = Maze(maze_size=9)
    assert not maze.is_inside(BoardLocation(14, -14))
    assert not maze.is_inside(BoardLocation(5, 9))

def _assert_sorted_board_locations(maze_locations):
    assert maze_locations[0] == BoardLocation(0, 0)
    length = len(maze_locations)
    for first, second in zip(range(length), range(1, length)):
        first_location = maze_locations[first]
        second_location = maze_locations[second]
        assert (first_location.row < second_location.row) or \
                ((first_location.row == second_location.row) and \
                (first_location.column < second_location.column))
