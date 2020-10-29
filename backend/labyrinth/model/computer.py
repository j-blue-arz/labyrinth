""" This module implements functionality for a computer to play the game.

ComputerPlayer is a subclass of model.game.Player, which handles board state and time-keeping.
The computation of player actions is performed by external shared libraries (LibraryBinding).
Clients should use the factory method create_computer_player() to create a ComputerPlayer instance.
"""

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
import labyrinth.model.external_library as extlib
from labyrinth.model import exceptions
from .reachable import Graph
from .game import Player, Turns


def create_computer_player(player_id, compute_method,
                           url_supplier=None, game=None, shift_url=None, move_url=None, piece=None):
    """ This is a factory method creating a ComputerPlayer.

    :param player_id: the identifier of the player to create.
    :param compute_method: is used to determine the action computation method and its parameters.
        It is expected to denote the filename of a shared library.
    :param url_supplier: a supplier for the shift and move API URLs.
        This supplier is expected to have methods get_shift_url(game_id, player_id), and
        get_move_url(game_id, player_id).
    :param shift_url: use this instead of url_supplier, if you already know the final url to call for a shift.
    :param move_url: use this instead of url_supplier, if you already know the final url to call for a move.
    :raises InvalidComputeMethodException: if compute_method cannot identify an existing library.
    """
    library_binding_factory = _library_binding_factory(expected_library=compute_method)
    return ComputerPlayer(library_binding_factory, url_supplier=url_supplier,
                          shift_url=shift_url, move_url=move_url,
                          identifier=player_id, game=game, piece=piece)


def get_available_computation_methods():
    """ Returns the identifiers of the available computation methods.
    All base filenames (without extension) in the
    library folder are returned.
    """
    def extract_basename(filename):
        basename, ext = os.path.splitext(os.path.basename(filename))
        return basename

    filenames = _library_filenames()
    return [extract_basename(filename) for filename in filenames]


class ComputerPlayer(Player, Thread):
    """ This class represents a computer player.

    If the player is requested to make its action, it starts a thread for time keeping,
    and a thread for letting the compute method determine the next shift and move action.
    Computation methods are time-restricted. After the computation timeout, they will be asked to abort.
    They will then receive a short grace period to finish their current work and return a result.
    :param library_binding_factory: a method creating a LibraryBinding,
        It is expected to take a board, a piece, and a game as its parameters.
    :param kwargs: keyword arguments, which are passed to the Player initializer.
     """

    COMPUTATION_TIMEOUT = timedelta(seconds=3)
    WAIT_FOR_RESULT = timedelta(milliseconds=100)
    MOVE_ACTION_IDLE_TIME = timedelta(seconds=2)

    def __init__(self, library_binding_factory, url_supplier=None, shift_url=None, move_url=None, **kwargs):
        Player.__init__(self, **kwargs)
        Thread.__init__(self)
        self._library_binding_factory = library_binding_factory
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
        compute_method = self._library_binding_factory(self._board, self._piece, self._game)
        compute_method.start()
        time.sleep(self.COMPUTATION_TIMEOUT.total_seconds())
        compute_method.abort_search()
        time.sleep(self.WAIT_FOR_RESULT.total_seconds())
        shift_action = compute_method.shift_action
        move_action = compute_method.move_action

        if shift_action is None or move_action is None:
            shift_action, move_action = self.random_actions()

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
        """ Getter for library_binding_factory, e.g. for serialization """
        return self._library_binding_factory

    def _post_shift(self, location, rotation):
        dto = labyrinth.mapper.api.shift_action_to_dto(location, rotation)
        requests.post(self.shift_url, json=dto)

    def _post_move(self, move_location):
        dto = labyrinth.mapper.api.move_action_to_dto(move_location)
        requests.post(self.move_url, json=dto)

    def random_actions(self):
        board = copy.deepcopy(self._board)
        piece = next(piece for piece in board.pieces if piece.maze_card.identifier == self._piece.maze_card.identifier)
        shift_location = choice(tuple(self._game.get_enabled_shift_locations()))
        shift_rotation = choice([0, 90, 180, 270])
        board.shift(shift_location, shift_rotation)
        piece_location = board.maze.maze_card_location(piece.maze_card)
        reachable_locations = Graph(board.maze).reachable_locations(piece_location)
        shift_action = (shift_location, shift_rotation)
        move_action = choice(tuple(reachable_locations))
        return shift_action, move_action


class LibraryBinding(Thread, extlib.ExternalLibraryBinding):
    """ Calls an external library to perform the move. The abort_search method is already
    implemented in the superclass. """

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


def _library_binding_factory(expected_library):
    library_folder = current_app.config['LIBRARY_PATH']
    extension = _library_extension()
    filenames = _library_filenames()
    full_library_path = None
    expected_filename = os.path.join(library_folder, expected_library + extension)
    for filename in filenames:
        if filename == expected_filename:
            full_library_path = filename
    if full_library_path:
        library_binding_factory = functools.partial(LibraryBinding,
                                                    full_library_path=full_library_path)
        setattr(library_binding_factory, "SHORT_NAME", expected_library)
        return library_binding_factory
    else:
        raise exceptions.InvalidComputeMethodException("Could not find library {}".format(expected_library))
