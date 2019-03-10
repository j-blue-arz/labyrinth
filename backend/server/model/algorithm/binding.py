import ctypes

class LOCATION(ctypes.Structure):
    """ corresponds to game.BoardLocation """
    _fields_ = [("row", ctypes.c_ushort), ("column", ctypes.c_ushort)]

class CARD(ctypes.Structure):
    """ corresponds to game.MazeCard
    The doors are represented as a bitfield """
    NORTH_DOOR = 1
    EAST_DOOR = 2
    SOUTH_DOOR = 4
    WEST_DOOR = 8
    DIRECTION_TO_DOOR = {(-1, 0): NORTH_DOOR, (0, 1): EAST_DOOR, (1, 0): SOUTH_DOOR, (0, -1): WEST_DOOR}
    _fields_ = [("doors", ctypes.c_ushort, 4)]

class GAME_STATE(ctypes.Structure):
    """ The input argument of the function call """
    _fields_ = [
        ("mazeSize", ctypes.c_uint),
        ("cardArray", CARD * 49),
        ("insertLocations", LOCATION * 12),
        ("previousInsert", LOCATION),
        ("pieceLocation", LOCATION),
        ("objectiveLocation", LOCATION),
        ("leftover", CARD)
    ]

def create_game_state(board, piece, previous_shift_location=None):
    """ creates a GAME_STATE function argument
    
    :param board: an instance of server.model.game.board
    :param piece: an instance of server.model.game.piece, has to be be a piece on the board
    :param previous_shift_location: the previous shift location, defaults to None. If present, it has to be
    one of board.insert_locations()
    """
    maze_size = board.maze.maze_size
    card_array = [create_card(board.maze[location]) for location in board.maze.maze_locations]
    insert_locations = [create_location(location) for location in board.insert_locations]

        

    return GAME_STATE(maze_size, (*card_array), (*insert_locations))

def create_card(maze_card):
    """ creates a CARD from a MazeCard """
    doors = 0
    for direction in maze_card.out_paths():
        doors = doors | CARD.DIRECTION_TO_DOOR[direction]
    return CARD(doors)

def create_location(board_location):
    """ creates a LOCATION from a BoardLocation """
    return LOCATION(board_location.row, board_location.column)

