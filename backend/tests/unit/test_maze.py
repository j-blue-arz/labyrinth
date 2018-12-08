""" Tests for Maze of model.py """
from domain.model import Maze, MazeCard, BoardLocation


def _get_id_matrix(board):
    """ Builds a matrix of the maze card identifiers of the given board """
    id_matrix = [[board[BoardLocation(row, column)].identifier
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
    board = Maze()
    maze_card = MazeCard()
    board[BoardLocation(1, 1)] = maze_card
    assert board[BoardLocation(1, 1)] == maze_card

def test_setter_does_not_alter_other_state():
    """ Tests setter and getter """
    board = Maze()
    board.generate_random()
    old_id_matrix = _get_id_matrix(board)
    board[BoardLocation(3, 3)] = MazeCard.generate_random()
    new_id_matrix = _get_id_matrix(board)
    difference = _compare_id_matrices(old_id_matrix, new_id_matrix)
    assert len(difference) == 1
    assert difference[0] == (3, 3)

def test_generate_random_generates_unique_ids_for_each_maze_card():
    """ Tests generate_random """
    board = Maze()
    board.generate_random()
    ids = set()
    for row in range(Maze.MAZE_SIZE):
        for column in range(Maze.MAZE_SIZE):
            current_id = board[BoardLocation(row, column)].identifier
            assert current_id not in ids
            ids.add(current_id)

def test_generate_random_fixes_corner_of_board():
    """ Tests generate_random """
    board = Maze()
    board.generate_random()
    extent = Maze.MAZE_SIZE - 1
    assert board[BoardLocation(0, 0)].doors == MazeCard.CORNER
    assert board[BoardLocation(0, 0)].rotation == 90
    assert board[BoardLocation(0, extent)].doors == MazeCard.CORNER
    assert board[BoardLocation(0, extent)].rotation == 180
    assert board[BoardLocation(extent, extent)].doors == MazeCard.CORNER
    assert board[BoardLocation(extent, extent)].rotation == 270
    assert board[BoardLocation(extent, 0)].doors == MazeCard.CORNER
    assert board[BoardLocation(extent, 0)].rotation == 0

def test_shift_inserts_leftover():
    """ Tests shift """
    board = Maze()
    board.generate_random()
    insertion = MazeCard.generate_random()
    board.shift(BoardLocation(0, 1), insertion)
    assert board[BoardLocation(0, 1)] == insertion

def test_shift_returns_pushed_out_card():
    """ Test shift """
    board = Maze()
    board.generate_random()
    opposite = board[BoardLocation(0, 3)]
    pushed_out = board.shift(BoardLocation(Maze.MAZE_SIZE - 1, 3), MazeCard.generate_random())
    assert opposite == pushed_out


def test_shift_alters_entire_row_correctly():
    """ Test shift """
    board = Maze()
    board.generate_random()
    old_id_matrix = _get_id_matrix(board)
    insertion = MazeCard.generate_random()
    board.shift(BoardLocation(5, Maze.MAZE_SIZE - 1), insertion)
    new_id_matrix = _get_id_matrix(board)
    assert new_id_matrix[5][Maze.MAZE_SIZE - 1] == insertion.identifier
    for col in range(Maze.MAZE_SIZE - 1):
        assert new_id_matrix[5][col] == old_id_matrix[5][col + 1]

def test_shift_does_not_alter_rest_of_board():
    """ Test shift """
    board = Maze()
    board.generate_random()
    old_id_matrix = _get_id_matrix(board)
    board.shift(BoardLocation(5, 0), MazeCard.generate_random())
    new_id_matrix = _get_id_matrix(board)
    differences = _compare_id_matrices(old_id_matrix, new_id_matrix)
    assert len(differences) == Maze.MAZE_SIZE
    for difference in differences:
        assert difference[0] == 5

def test_board_locations_returns_list_of_correct_size():
    """ Test maze_locations """
    maze_locations = [location for location in Maze.maze_locations()]
    assert len(maze_locations) == Maze.MAZE_SIZE * Maze.MAZE_SIZE

def test_board_locations_returns_list_of_all_board_locations():
    """ Test maze_locations """
    maze_locations = [location for location in Maze.maze_locations()]
    for row in range(Maze.MAZE_SIZE):
        for column in range(Maze.MAZE_SIZE):
            assert BoardLocation(row, column) in maze_locations

def test_board_locations_returns_list_in_ascending_order():
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
    board = Maze()
    board.generate_random()
    for location in Maze.maze_locations():
        assert board.maze_card_location(board[location]) == location

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
