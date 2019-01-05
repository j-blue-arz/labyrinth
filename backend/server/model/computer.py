""" This module implements functionality for a computer to play the game.
ComputerPlayer is a subclass of model.game.Player, which handles board state and time-keeping.
It uses an algorithm to compute a shift and a move.

These algorithms are implemented in a separate class, ending with 'Algorithm'.
The Algorithm classes are expected to have a getter for shift_action and move_action, with which they provide their
solutions for the respective moves.
shift_action is expected to return a tuple of the form (<insert_location>, <insert_rotation>),
where <insert_location> is a BoardLocation, <insert_rotation> is one of [0, 90, 270, 180]
move_action should return a BoardLocation  """

import copy
from random import choice
import time
from threading import Thread
import requests
import server.mapper.api
from .maze_algorithm import Graph
from .game import Player, Turns
from .search import Optimizer


class ComputerPlayer(Player, Thread):
    """ This class represents a computer player. It is instantiated with
    an algorithm_name parameter, either 'random' or 'exhaustive-single'. Default is 'exhaustive-single'.
    A second required parameter is a supplier for the shift and move API URLs.
    This supplier is expected to have methods get_shift_url(game_id, player_id), and
    get_move_url(game_id, player_id).

    If the player is requested to make its action, it starts a thread for time keeping,
    and a thread for letting the algorithm compute the next shift and move action. """

    _SECONDS_TO_ANSWER = 2

    def __init__(self, algorithm_name=None, url_supplier=None, move_url=None, shift_url=None, **kwargs):
        Player.__init__(self, **kwargs)
        Thread.__init__(self)
        algorithms = [RandomActionsAlgorithm, ExhaustiveSearchAlgorithm]
        self.algorithm = ExhaustiveSearchAlgorithm
        for algorithm in algorithms:
            if algorithm.SHORT_NAME == algorithm_name:
                self.algorithm = algorithm
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
        algorithm = self.algorithm(board, piece)
        algorithm.start()
        time.sleep(self._SECONDS_TO_ANSWER)
        shift_action = algorithm.shift_action
        move_action = algorithm.move_action

        if shift_action is None or move_action is None:
            algorithm.abort_search()
            board = copy.deepcopy(self._board)
            piece = self._find_equal_piece(board)
            fallback_algorithm = RandomActionsAlgorithm(board, piece, self._game.get_enabled_shift_locations())
            # Calling run directly, so that fallback waits for algorithm to finish before posting actions
            fallback_algorithm.run()
            shift_action = fallback_algorithm.shift_action
            move_action = fallback_algorithm.move_action
        self._post_shift(*shift_action)
        time.sleep(self._SECONDS_TO_ANSWER)
        self._post_move(move_action)

    @property
    def shift_url(self):
        """ Getter for shift_url """
        return self._shift_url

    @property
    def move_url(self):
        """ Getter for move_url """
        return self._move_url

    def _post_shift(self, insert_location, insert_rotation):
        dto = server.mapper.api.shift_action_to_dto(insert_location, insert_rotation)
        requests.post(self.shift_url, json=dto)

    def _post_move(self, move_location):
        dto = server.mapper.api.move_action_to_dto(move_location)
        requests.post(self.move_url, json=dto)

    def _find_equal_piece(self, board):
        return next(piece for piece in board.pieces if piece.maze_card.identifier == self._piece.maze_card.identifier)


class RandomActionsAlgorithm(Thread):
    """ Implements an algorithm which performs a random shift action followed by a random, but valid
    move action """

    SHORT_NAME = "random"

    def __init__(self, board, piece, enabled_shift_locations=None):
        super().__init__()
        self._board = board
        self._maze = board.maze
        self._piece = piece
        self._shift_action = None
        self._move_action = None
        if enabled_shift_locations:
            self._enabled_shift_locations = enabled_shift_locations
        else:
            self._enabled_shift_locations = self._board.insert_locations

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
        pass

    def run(self):
        insert_location = choice(tuple(self._enabled_shift_locations))
        insert_rotation = choice([0, 90, 180, 270])
        self._shift_action = (insert_location, insert_rotation)
        self._board.shift(insert_location, insert_rotation)
        piece_location = self._maze.maze_card_location(self._piece.maze_card)
        reachable_locations = Graph(self._maze).reachable_locations(piece_location)
        self._move_action = choice(tuple(reachable_locations))


class ExhaustiveSearchAlgorithm(Thread, Optimizer):
    """ Uses an exhaustive search to compute best single-player solution to objective.
    abort_search() is already implemented in superclass, Optimizer. """
    SHORT_NAME = "exhaustive-single"

    def __init__(self, board, piece):
        Optimizer.__init__(self, board, piece)
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
