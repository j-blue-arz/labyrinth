""" This module provides a binding to an external library.

It models the structs with ctypes and defines a class which implements the algorithm interface by
binding to a library at a given path """
import ctypes
from labyrinth.model.game import BoardLocation


class LOCATION(ctypes.Structure):
    """ corresponds to game.BoardLocation """
    _fields_ = [("row", ctypes.c_short), ("column", ctypes.c_short)]


class PLAYER_LOCATIONS(ctypes.Structure):
    """ an array of locations """
    _fields_ = [("locations", ctypes.POINTER(LOCATION)), ("num_players", ctypes.c_ulong)]


class NODE(ctypes.Structure):
    """ corresponds to game.MazeCard
    The out_paths are represented as a bitfield """
    _fields_ = [("node_id", ctypes.c_uint), ("out_paths", ctypes.c_ubyte), ("rotation", ctypes.c_short)]


class GRAPH(ctypes.Structure):
    """ corresponds to game.Maze """
    _fields_ = [
        ("extent", ctypes.c_long),
        ("num_nodes", ctypes.c_ulong),
        ("nodes", ctypes.POINTER(NODE))
    ]


class ACTION(ctypes.Structure):
    """ return type of algolibs function call: shift location, rotation and move location """
    _fields_ = [
        ("shift_location", LOCATION),
        ("rotation", ctypes.c_short),
        ("move_location", LOCATION),
    ]


class STATUS(ctypes.Structure):
    """ Search status of the current search. """
    _fields_ = [
        ("current_search_depth", ctypes.c_ulong),
        ("search_terminated", ctypes.c_bool)
    ]


class ExternalLibraryBinding:
    """ Binds to an external library at given path.
    Translates the game datastructures to the ctypes structures and back """
    _OUT_PATH_TO_BIT = {"N": 1, "E": 2, "S": 4, "W": 8}

    _ERROR_LOCATION = BoardLocation(-1, -1)

    def __init__(self, path, board, piece, previous_shift_location=None):
        self._library = ctypes.cdll.LoadLibrary(path)
        self._library.find_action.restype = ACTION
        self._library.abort_search.restype = None
        self._library.get_status.restype = STATUS
        self._board = board
        pos = board.pieces.index(piece)
        self._pieces = board.pieces[pos:] + board.pieces[:pos]
        self._previous_shift_location = previous_shift_location
        if self._previous_shift_location is None:
            self._previous_shift_location = BoardLocation(-1, -1)

    def find_optimal_action(self):
        """ finds optimal action by calling the external library """
        graph = self._create_graph(self._board)
        start_locations = [self._board.maze.maze_card_location(piece.maze_card) for piece in self._pieces]
        start_locations = self._create_player_locations(start_locations)
        previous_shift_location = self._create_location(self._previous_shift_location)
        objective_id = self._board.objective_maze_card.identifier
        action = self._library.find_action(ctypes.byref(graph), ctypes.byref(start_locations), objective_id,
                                           ctypes.byref(previous_shift_location))
        return self._map_returned_action(action)

    def abort_search(self):
        self._library.abort_search()

    def get_search_status(self):
        status = self._library.get_status()
        return self._map_search_status(status)

    @staticmethod
    def _create_node(maze_card):
        """ creates a NODE from a MazeCard """
        out_paths = 0
        for out_path in maze_card.out_paths:
            out_paths |= ExternalLibraryBinding._OUT_PATH_TO_BIT[out_path]
        return NODE(maze_card.identifier, out_paths, maze_card.rotation)

    @staticmethod
    def _create_graph(board):
        """ creates a GRAPH function argument

        :param board: an instance of labyrinth.model.game.board
        """
        maze = board.maze
        extent = maze.maze_size
        node_array = [ExternalLibraryBinding._create_node(maze[location]) for location in maze.maze_locations]
        node_array.append(ExternalLibraryBinding._create_node(board.leftover_card))
        nodes = (NODE * len(node_array))(*node_array)
        return GRAPH(extent=extent, num_nodes=len(node_array), nodes=nodes)

    @staticmethod
    def _create_location(board_location):
        """ creates a LOCATION from a BoardLocation """
        return LOCATION(board_location.row, board_location.column)

    @classmethod
    def _map_returned_action(cls, action):
        """ creates an action tuple (shift_location, rotation), move_location from an ACTION """
        shift_location = BoardLocation(action.shift_location.row, action.shift_location.column)
        move_location = BoardLocation(action.move_location.row, action.move_location.column)
        if shift_location != cls._ERROR_LOCATION and move_location != cls._ERROR_LOCATION:
            return (shift_location, action.rotation), move_location
        else:
            return None

    @classmethod
    def _create_player_locations(cls, board_locations):
        """ creates a PLAYER_LOCATIONS from a list of BoardLocations """
        location_array = [ExternalLibraryBinding._create_location(location) for location in board_locations]
        player_locations = (LOCATION * len(location_array))(*location_array)
        return PLAYER_LOCATIONS(locations=player_locations, num_players=len(location_array))

    @classmethod
    def _map_search_status(cls, status):
        """ creates a dict from a STATUS """
        return {"current_search_depth": status.current_search_depth, "search_terminated": status.search_terminated}
