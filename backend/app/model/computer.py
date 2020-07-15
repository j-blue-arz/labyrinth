""" This module implements functionality for a computer to play the game.
ComputerPlayer is a subclass of model.game.Player, which handles board state and time-keeping.
It uses an algorithm to compute a shift and a move.

These algorithms are implemented in a separate class, ending with 'Algorithm'.
The Algorithm classes are expected to have a getter for shift_action and move_action, with which they provide their
solutions for the respective moves.
shift_action is expected to return a tuple of the form (<shift_location>, <shift_rotation>),
where <shift_location> is a BoardLocation, <shift_rotation> is one of [0, 90, 270, 180]
move_action should return a BoardLocation  """

import copy
from random import choice
import time
from threading import Thread
import os
from flask import current_app
import requests
import app.mapper.api
import app.model.algorithm.exhaustive_search as exh
import app.model.algorithm.minimax as mm
import app.model.algorithm.alpha_beta as ab
import app.model.algorithm.external_library as extlib
from .reachable import Graph
from .game import Player, Turns
from .exceptions import LabyrinthDomainException
from .factories import maze_to_string


class ComputerPlayer(Player, Thread):
    """ This class represents a computer player. It is instantiated with
    an algorithm_name parameter, either 'random', 'exhaustive-search', or 'minimax'. Default is 'exhaustive-search'.
    A second required parameter is a supplier for the shift and move API URLs.
    This supplier is expected to have methods get_shift_url(game_id, player_id), and
    get_move_url(game_id, player_id).

    If the player is requested to make its action, it starts a thread for time keeping,
    and a thread for letting the algorithm compute the next shift and move action. """

    _SECONDS_TO_ANSWER = 1.5

    def __init__(self, algorithm_name=None, url_supplier=None, move_url=None, shift_url=None, **kwargs):
        Player.__init__(self, **kwargs)
        Thread.__init__(self)
        algorithms = [RandomActionsAlgorithm, ExhaustiveSearchAlgorithm,
                      MinimaxAlgorithm, AlphaBetaAlgorithm, LibraryBinding]
        self.algorithm = ExhaustiveSearchAlgorithm
        for algorithm in algorithms:
            if algorithm.SHORT_NAME == algorithm_name:
                self.algorithm = algorithm
        if current_app:
            self._app = current_app._get_current_object()
        else:
            self._app = None
        if url_supplier:
            self._shift_url = url_supplier.get_shift_url(self._game.identifier, self._id)
            self._move_url = url_supplier.get_move_url(self._game.identifier, self._id)
        elif move_url and shift_url:
            self._shift_url = shift_url
            self._move_url = move_url
        else:
            raise ValueError("Either url_supplier, or move_url and shift_url have to be given as parameters.")

    def register_in_turns(self, turns: Turns):
        """ Registers itself in a Turns manager.
        Overwrites superclass method. """
        turns.add_player(self, turn_callback=self.start)

    def run(self):
        board = copy.deepcopy(self._board)
        piece = self._find_equal_piece(board)
        algorithm = self.algorithm(board, piece, self._game, current_app=self._app)
        algorithm.start()
        time.sleep(algorithm.SECONDS_TO_COMPUTE)
        time.sleep(self._SECONDS_TO_ANSWER)
        shift_action = algorithm.shift_action
        move_action = algorithm.move_action

        if shift_action is None or move_action is None:
            board = copy.deepcopy(self._board)
            piece = self._find_equal_piece(board)
            fallback_algorithm = RandomActionsAlgorithm(board, piece, self._game)
            # Calling run directly, so that fallback waits for algorithm to finish before posting actions
            fallback_algorithm.run()
            shift_action = fallback_algorithm.shift_action
            move_action = fallback_algorithm.move_action

        # self._validate(shift_action, move_action)
        self._post_shift(*shift_action)
        time.sleep(self._SECONDS_TO_ANSWER)
        self._post_move(move_action)
        algorithm.abort_search()

    @property
    def shift_url(self):
        """ Getter for shift_url """
        return self._shift_url

    @property
    def move_url(self):
        """ Getter for move_url """
        return self._move_url

    def _post_shift(self, location, rotation):
        dto = app.mapper.api.shift_action_to_dto(location, rotation)
        requests.post(self.shift_url, json=dto)

    def _post_move(self, move_location):
        dto = app.mapper.api.move_action_to_dto(move_location)
        requests.post(self.move_url, json=dto)

    def _find_equal_piece(self, board):
        return next(piece for piece in board.pieces if piece.maze_card.identifier == self._piece.maze_card.identifier)

    def _validate(self, shift_action, move_action):
        board = copy.deepcopy(self._board)
        piece = self._find_equal_piece(board)

        maze_string = maze_to_string(board.maze)
        piece_locations = [board.maze.maze_card_location(piece.maze_card) for piece in board.pieces]
        self_location = board.maze.maze_card_location(piece.maze_card)
        objective_location = board.maze.maze_card_location(board.objective_maze_card)
        try:
            shift_location, rotation = shift_action
            self._game._validate_pushback_rule(shift_location)
            board.shift(shift_location, rotation)
            self_location = board.maze.maze_card_location(piece.maze_card)
            board._validate_move_location(self_location, move_action)
        except LabyrinthDomainException as exc:
            print(exc)
            print("piece locations: {}".format(piece_locations))
            print("self location: {}".format(self_location))
            print("objective location: {}".format(objective_location))
            print("shift_action: {}, move_action: {}".format(shift_action, move_action))
            print(maze_string)


class RandomActionsAlgorithm(Thread):
    """ Implements an algorithm which performs a random shift action followed by a random, but valid
    move action """

    SHORT_NAME = "random"
    SECONDS_TO_COMPUTE = 0.5

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


class ExhaustiveSearchAlgorithm(Thread, exh.Optimizer):
    """ Uses an exhaustive search to compute best single-player solution to objective.
    abort_search() is already implemented in superclass, exh.Optimizer. """
    SHORT_NAME = "exhaustive-search"
    SECONDS_TO_COMPUTE = 1.5

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


class MinimaxAlgorithm(Thread, mm.IterativeDeepening):
    """ Uses the minimax algorithm to determine an action in a two-player game. """
    SHORT_NAME = "minimax"
    SECONDS_TO_COMPUTE = 2.5

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


class AlphaBetaAlgorithm(Thread, ab.IterativeDeepening):
    """ Uses the minimax algorithm to determine an action in a two-player game. """
    SHORT_NAME = "alpha-beta"
    SECONDS_TO_COMPUTE = 2.5

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
    SHORT_NAME = "library"
    SECONDS_TO_COMPUTE = 1.5

    def __init__(self, board, piece, game, library_dll="libexhsearch.so", **kwargs):
        library_path_to_dll = os.path.join(kwargs["current_app"].config['LIBRARY_PATH'], library_dll)
        extlib.ExternalLibraryBinding.__init__(self, library_path_to_dll,
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
