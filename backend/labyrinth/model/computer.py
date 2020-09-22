""" This module implements functionality for a computer to play the game.

ComputerPlayer is a subclass of model.game.Player, which handles board state and time-keeping.
The other classes represent different methods of computing player actions. They either
compute the action on their own (e.g. RandomActionsMethod), or subclass an algorithm implementation
from labyrinth.model.algorithm (e.g. AlphaBeta), or bind to an external library (LibraryBinding).

Clients should use the factory method create_computer_player() to create a ComputerPlayer instance.

The computation method classes are expected to have a getter for shift_action and move_action,
with which they provide their solutions for the respective moves.
shift_action is expected to return a tuple of the form (<shift_location>, <shift_rotation>),
where <shift_location> is a BoardLocation, <shift_rotation> is one of [0, 90, 270, 180]
move_action should return a BoardLocation.  """

import copy
import functools
import glob
from datetime import timedelta
import os
from random import choice
import time
from threading import Thread
import platform

from flask import current_app
import requests

import labyrinth.mapper.api
import labyrinth.model.algorithm.exhaustive_search as exh
import labyrinth.model.algorithm.minimax as mm
import labyrinth.model.algorithm.alpha_beta as ab
import labyrinth.model.algorithm.external_library as extlib
from labyrinth.model import exceptions
from .reachable import Graph
from .game import Player, Turns


def create_computer_player(player_id, compute_method,
                           url_supplier=None, game=None, shift_url=None, move_url=None, piece=None):
    """ This is a factory method creating a ComputerPlayer.

    :param player_id: the identifier of the player to create.
    :param compute_method: is used to determine the action computation method and its parameters.
        If this parameter starts with 'dynamic-', it is expected to denote a shared library.
        Otherwise, it has to match one of the computation methods implemented in the backend currently
        'random', 'exhaustive-search', 'minimax', or 'alpha-beta'.
    :param url_supplier: a supplier for the shift and move API URLs.
        This supplier is expected to have methods get_shift_url(game_id, player_id), and
        get_move_url(game_id, player_id).
    :param shift_url: use this instead of url_supplier, if you already know the final url to call for a shift.
    :param move_url: use this instead of url_supplier, if you already know the final url to call for a move.
    :raises InvalidComputeMethodException: if compute_method cannot identify an existing computation method.
    """
    library_prefix = LibraryBinding.LIBRARY_PREFIX
    compute_method_factory = None
    if compute_method.startswith(library_prefix):
        compute_method_factory = _dynamic_compute_method_factory(compute_method)
    else:
        compute_method_factory = _backend_compute_method_factory(compute_method)
    return ComputerPlayer(compute_method_factory, url_supplier=url_supplier,
                          shift_url=shift_url, move_url=move_url,
                          identifier=player_id, game=game, piece=piece)


def get_available_computation_methods():
    """ Returns the identifiers of the available computation methods.
    The methods implemented in the backend are hard-coded.
    For the dynamically loaded libraries, all base filenames (without extension) in the
    library folder are returned, each prefixed with 'dynamic-'.
    """
    def extract_basename(filename):
        basename, ext = os.path.splitext(os.path.basename(filename))
        return basename

    backend_computation_methods = [method.SHORT_NAME for method in _backend_computation_methods()]
    filenames = _library_filenames()
    prefix = LibraryBinding.LIBRARY_PREFIX
    dynamic_computation_methods = [prefix + extract_basename(filename) for filename in filenames]
    return backend_computation_methods + dynamic_computation_methods


class ComputerPlayer(Player, Thread):
    """ This class represents a computer player.

    If the player is requested to make its action, it starts a thread for time keeping,
    and a thread for letting the compute method determine the next shift and move action.
    Computation methods are time-restricted. After the computation timeout, they will be asked to abort.
    They will then receive a short grace period to finish their current work and return a result.
    :param compute_method_factory: a method creating a computation method,
        i.e. one of the other classes in this module.
        It is expected to take a board, a piece, and a game as its parameters.
    :param kwargs: keyword arguments, which are passed to the Player initializer.
     """

    COMPUTATION_TIMEOUT = timedelta(seconds=3)
    WAIT_FOR_RESULT = timedelta(milliseconds=100)
    MOVE_ACTION_IDLE_TIME = timedelta(seconds=2)

    def __init__(self, compute_method_factory, url_supplier=None, shift_url=None, move_url=None, **kwargs):
        Player.__init__(self, **kwargs)
        Thread.__init__(self)
        self._compute_method_factory = compute_method_factory
        self._shift_url = shift_url
        self._move_url = move_url
        self._url_supplier = url_supplier
        self._set_urls()

    def register_in_turns(self, turns: Turns):
        """ Registers itself in a Turns manager.
        Overwrites superclass method. """
        turns.add_player(self, turn_callback=self.start)

    def set_game(self, game):
        """ Sets the API urls.
        Overwrites superclass method. """
        Player.set_game(self, game)
        self._set_urls()

    def _set_urls(self):
        if self._game:
            if not self._shift_url:
                self._shift_url = self._url_supplier.get_shift_url(self._game.identifier, self.identifier)
            if not self._move_url:
                self._move_url = self._url_supplier.get_move_url(self._game.identifier, self.identifier)

    def run(self):
        board = copy.deepcopy(self._board)
        piece = self._find_equal_piece(board)
        compute_method = self._compute_method_factory(board, piece, self._game)
        compute_method.start()
        time.sleep(self.COMPUTATION_TIMEOUT.total_seconds())
        compute_method.abort_search()
        time.sleep(self.WAIT_FOR_RESULT.total_seconds())
        shift_action = compute_method.shift_action
        move_action = compute_method.move_action

        if shift_action is None or move_action is None:
            board = copy.deepcopy(self._board)
            piece = self._find_equal_piece(board)
            fallback = RandomActionsMethod(board, piece, self._game)
            # Calling run directly, so that fallback waits for computation to finish before posting actions
            fallback.run()
            shift_action = fallback.shift_action
            move_action = fallback.move_action

        # self._validate(shift_action, move_action)
        self._post_shift(*shift_action)
        time.sleep(self.MOVE_ACTION_IDLE_TIME.total_seconds())
        self._post_move(move_action)

    @property
    def shift_url(self):
        """ Getter for shift_url """
        return self._shift_url

    @property
    def move_url(self):
        """ Getter for move_url """
        return self._move_url

    @property
    def compute_method_factory(self):
        """ Getter for compute_method_factory, e.g. for serialization """
        return self._compute_method_factory

    def _post_shift(self, location, rotation):
        dto = labyrinth.mapper.api.shift_action_to_dto(location, rotation)
        requests.post(self.shift_url, json=dto)

    def _post_move(self, move_location):
        dto = labyrinth.mapper.api.move_action_to_dto(move_location)
        requests.post(self.move_url, json=dto)

    def _find_equal_piece(self, board):
        return next(piece for piece in board.pieces if piece.maze_card.identifier == self._piece.maze_card.identifier)
    
    def _validate(self, shift_action, move_action):
        board = copy.deepcopy(self._board)
        piece = self._find_equal_piece(board)

        piece_locations = [board.maze.maze_card_location(piece.maze_card) for piece in board.pieces]
        self_location = board.maze.maze_card_location(piece.maze_card)
        objective_location = board.maze.maze_card_location(board.objective_maze_card)
        try:
            shift_location, rotation = shift_action
            self._game._validate_pushback_rule(shift_location)
            board.shift(shift_location, rotation)
            self_location = board.maze.maze_card_location(piece.maze_card)
            board._validate_move_location(self_location, move_action)
        except exceptions.LabyrinthDomainException as exc:
            print(exc)
            print("piece locations: {}".format(piece_locations))
            print("self location: {}".format(self_location))
            print("objective location: {}".format(objective_location))
            print("shift_action: {}, move_action: {}".format(shift_action, move_action))


class RandomActionsMethod(Thread):
    """ Implements a computation method which performs a random shift action followed by a random, but valid
    move action """

    SHORT_NAME = "random"

    def __init__(self, board, piece, game, **kwargs):
        super().__init__()
        self._board = board
        self._maze = board.maze
        self._piece = piece
        self._shift_action = None
        self._move_action = None
        self._enabled_shift_locations = game.get_enabled_shift_locations()

    @property
    def shift_action(self):
        """ Getter for shift_action """
        return self._shift_action

    @property
    def move_action(self):
        """ Getter for move_action """
        return self._move_action

    def abort_search(self):
        """ To fulfill the interface """

    def run(self):
        shift_location = choice(tuple(self._enabled_shift_locations))
        shift_rotation = choice([0, 90, 180, 270])
        self._shift_action = (shift_location, shift_rotation)
        self._board.shift(shift_location, shift_rotation)
        piece_location = self._maze.maze_card_location(self._piece.maze_card)
        reachable_locations = Graph(self._maze).reachable_locations(piece_location)
        self._move_action = choice(tuple(reachable_locations))


class ExhaustiveSearch(Thread, exh.Optimizer):
    """ Uses an exhaustive search to compute best single-player solution to objective.
    abort_search() is already implemented in superclass, exh.Optimizer. """
    SHORT_NAME = "exhaustive-search"

    def __init__(self, board, piece, game, **kwargs):
        exh.Optimizer.__init__(self, board, piece, game.previous_shift_location)
        Thread.__init__(self)
        self._shift_action = None
        self._move_action = None

    @property
    def shift_action(self):
        """ Getter for shift_action """
        return self._shift_action

    @property
    def move_action(self):
        """ Getter for move_action """
        return self._move_action

    def run(self):
        actions = self.find_optimal_actions()
        if actions:
            self._shift_action = actions[0]
            self._move_action = actions[1]


class Minimax(Thread, mm.IterativeDeepening):
    """ Uses the minimax algorithm to determine an action in a two-player game. """
    SHORT_NAME = "minimax"

    def __init__(self, board, player_piece, game, **kwargs):
        other_piece = next(piece for piece in board.pieces if piece is not player_piece)
        pieces = [player_piece, other_piece]
        mm.IterativeDeepening.__init__(self, board, pieces, game.previous_shift_location)
        Thread.__init__(self)

    @property
    def shift_action(self):
        """ Getter for shift_action """
        return self._shift_action

    @property
    def move_action(self):
        """ Getter for move_action """
        return self._move_action

    def abort_search(self):
        """ Aborts the search """
        self.stop_iterating()

    def run(self):
        self.start_iterating()


class AlphaBeta(Thread, ab.IterativeDeepening):
    """ Uses the alpha-beta algorithm to determine an action in a two-player game. """
    SHORT_NAME = "alpha-beta"

    def __init__(self, board, player_piece, game, **kwargs):
        self._board = board
        other_piece = next(piece for piece in board.pieces if piece is not player_piece)
        self._pieces = [player_piece, other_piece]
        self._game = game
        ab.IterativeDeepening.__init__(self)
        Thread.__init__(self)

    @property
    def shift_action(self):
        """ Getter for shift_action """
        return self._shift_action

    @property
    def move_action(self):
        """ Getter for move_action """
        return self._move_action

    def abort_search(self):
        """ Aborts the search """
        self.stop_iterating()

    def run(self):
        self.start_iterating(self._board, self._pieces, self._game.previous_shift_location)


class LibraryBinding(Thread, extlib.ExternalLibraryBinding):
    """ Calls an external library to perform the move. Random move as fallback """
    LIBRARY_PREFIX = "dynamic-"

    def __init__(self, board, piece, game, full_library_path):
        extlib.ExternalLibraryBinding.__init__(self, full_library_path,
                                               board, piece, game.previous_shift_location)
        Thread.__init__(self)
        self._shift_action = None
        self._move_action = None

    @property
    def shift_action(self):
        """ Getter for shift_action """
        return self._shift_action

    @property
    def move_action(self):
        """ Getter for move_action """
        return self._move_action

    def abort_search(self):
        """ not abortable, hence pass """

    def run(self):
        action = self.find_optimal_action()
        if action:
            self._shift_action = action[0]
            self._move_action = action[1]


def _library_extension():
    extension = ".so"
    if platform.system() == "Windows":
        extension = ".dll"
    return extension


def _library_filenames():
    library_folder = current_app.config['LIBRARY_PATH']
    extension = _library_extension()
    search_pattern = os.path.join(library_folder, '*' + extension)
    return glob.glob(search_pattern)


def _dynamic_compute_method_factory(compute_method):
    library_prefix = LibraryBinding.LIBRARY_PREFIX
    expected_library = compute_method[len(library_prefix):]
    library_folder = current_app.config['LIBRARY_PATH']
    extension = _library_extension()
    filenames = _library_filenames()
    full_library_path = None
    expected_filename = os.path.join(library_folder, expected_library + extension)
    for filename in filenames:
        if filename == expected_filename:
            full_library_path = filename
    if full_library_path:
        compute_method_factory = functools.partial(LibraryBinding,
                                                   full_library_path=full_library_path)
        setattr(compute_method_factory, "SHORT_NAME", library_prefix + expected_library)
        return compute_method_factory
    else:
        raise exceptions.InvalidComputeMethodException("Could not find library {}".format(expected_library))


def _backend_computation_methods():
    return [RandomActionsMethod, ExhaustiveSearch,
            Minimax, AlphaBeta]


def _backend_compute_method_factory(compute_method):
    compute_method_factory = None
    compute_method_classes = _backend_computation_methods()
    for method_class in compute_method_classes:
        if method_class.SHORT_NAME == compute_method:
            compute_method_factory = method_class
    if not compute_method_factory:
        raise exceptions.InvalidComputeMethodException("Could not find compute method {}".format(compute_method))
    return compute_method_factory
