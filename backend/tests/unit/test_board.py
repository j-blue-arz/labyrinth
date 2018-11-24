""" Tests for Board of model.py """
from domain.model import Board, MazeCard, BoardLocation


def _get_id_matrix(board):
    """ Builds a matrix of the maze card identifiers of the given board """
    id_matrix = [[board[BoardLocation(row, column)].identifier
                  for column in range(Board.BOARD_SIZE)]
                 for row in range(Board.BOARD_SIZE)]
    return id_matrix

def _compare_id_matrices(id_matrix_1, id_matrix_2):
    """ Returns all indices (x, y) where id_matrix_1[x][y] != id_matrix_2[x][y] """
    result = []
    for row in range(Board.BOARD_SIZE):
        for column in range(Board.BOARD_SIZE):
            if id_matrix_1[row][column] != id_matrix_2[row][column]:
                result.append((row, column))
    return result

def test_getter_returns_set_card():
    """ Tests setter and getter """
    board = Board()
    maze_card = MazeCard()
    board[BoardLocation(1, 1)] = maze_card
    assert board[BoardLocation(1, 1)] == maze_card

def test_setter_does_not_alter_other_state():
    """ Tests setter and getter """
    board = Board()
    board.generate_random()
    old_id_matrix = _get_id_matrix(board)
    board[BoardLocation(3, 3)] = MazeCard.generate_random()
    new_id_matrix = _get_id_matrix(board)
    difference = _compare_id_matrices(old_id_matrix, new_id_matrix)
    assert len(difference) == 1
    assert difference[0] == (3, 3)

def test_generate_random_generates_unique_ids_for_each_maze_card():
    """ Tests generate_random """
    board = Board()
    board.generate_random()
    ids = set()
    for row in range(Board.BOARD_SIZE):
        for column in range(Board.BOARD_SIZE):
            current_id = board[BoardLocation(row, column)].identifier
            assert current_id not in ids
            ids.add(current_id)

def test_shift_inserts_leftover():
    """ Tests shift """
    board = Board()
    board.generate_random()
    insertion = MazeCard.generate_random()
    board.shift(BoardLocation(0, 1), insertion)
    assert board[BoardLocation(0, 1)] == insertion

def test_shift_returns_pushed_out_card():
    """ Test shift """
    board = Board()
    board.generate_random()
    opposite = board[BoardLocation(0, 3)]
    pushed_out = board.shift(BoardLocation(Board.BOARD_SIZE - 1, 3), MazeCard.generate_random())
    assert opposite == pushed_out


def test_shift_alters_entire_row_correctly():
    """ Test shift """
    board = Board()
    board.generate_random()
    old_id_matrix = _get_id_matrix(board)
    insertion = MazeCard.generate_random()
    board.shift(BoardLocation(5, Board.BOARD_SIZE - 1), insertion)
    new_id_matrix = _get_id_matrix(board)
    assert new_id_matrix[5][Board.BOARD_SIZE - 1] == insertion.identifier
    for col in range(Board.BOARD_SIZE - 1):
        assert new_id_matrix[5][col] == old_id_matrix[5][col + 1]

def test_shift_does_not_alter_rest_of_board():
    """ Test shift """
    board = Board()
    board.generate_random()
    old_id_matrix = _get_id_matrix(board)
    board.shift(BoardLocation(5, 0), MazeCard.generate_random())
    new_id_matrix = _get_id_matrix(board)
    differences = _compare_id_matrices(old_id_matrix, new_id_matrix)
    assert len(differences) == Board.BOARD_SIZE
    for difference in differences:
        assert difference[0] == 5

def test_board_locations_returns_list_of_correct_size():
    """ Test board_locations """
    board_locations = Board.board_locations()
    assert len(board_locations) == Board.BOARD_SIZE * Board.BOARD_SIZE

def test_board_locations_returns_list_of_all_board_locations():
    """ Test board_locations """
    board_locations = Board.board_locations()
    for row in range(Board.BOARD_SIZE):
        for column in range(Board.BOARD_SIZE):
            assert BoardLocation(row, column) in board_locations

def test_board_locations_returns_list_in_ascending_order():
    """ Test board_locations """
    board_locations = Board.board_locations()
    length = len(board_locations)
    assert board_locations[0] == BoardLocation(0, 0)
    for first, second in zip(range(length), range(1, length)):
        first_location = board_locations[first]
        second_location = board_locations[second]
        assert (first_location.row < second_location.row) or \
                ((first_location.row == second_location.row) and \
                (first_location.column < second_location.column))
