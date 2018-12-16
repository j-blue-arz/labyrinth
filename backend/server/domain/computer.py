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
from flask import url_for
import requests
from .maze_algorithm import Graph
from .model import Player, Turns
from ..mapper.api import shift_action_to_dto, move_action_to_dto


class ComputerPlayer(Player, Thread):
    """ This class represents a computer player. It is instantiated with
    an algorithm parameter, currently only 'random' is implemented. Defaults to 'random'.
    If the player is requested to make its action, it starts a thread for time keeping,
    and a thread for letting the algorithm compute the next shift and move action """

    _SECONDS_TO_ANSWER = 3

    def __init__(self, algorithm_name, **kwargs):
        Player.__init__(self, **kwargs)
        Thread.__init__(self)
        algorithms = [RandomActionsAlgorithm]
        self.algorithm = RandomActionsAlgorithm
        for algorithm in algorithms:
            if algorithm.SHORT_NAME == algorithm_name:
                self.algorithm = algorithm
        self._shift_url = url_for("api.post_shift", game_id=self._game_id,
                                  p_id=self._id, _external=True)
        self._move_url = url_for("api.post_move", game_id=self._game_id,
                                 p_id=self._id, _external=True)

    def register_in_turns(self, turns: Turns):
        """ Registers itself in a Turns manager.
        Overwrites superclass method. """
        turns.add_player(self, turn_callback=self.start)

    def run(self):
        self._board = copy.deepcopy(self._board)
        algorithm = self.algorithm(self._board, self._piece)
        algorithm.start()
        time.sleep(self._SECONDS_TO_ANSWER)
        self._post_shift(*(algorithm.shift_action))
        time.sleep(self._SECONDS_TO_ANSWER)
        self._post_move(algorithm.move_action)

    def _post_shift(self, insert_location, insert_rotation):
        dto = shift_action_to_dto(insert_location, insert_rotation)
        requests.post(self._shift_url, json=dto)

    def _post_move(self, move_location):
        dto = move_action_to_dto(move_location)
        requests.post(self._move_url, json=dto)


class RandomActionsAlgorithm(Thread):
    """ Implements an algorithm which performs a random shift action followed by a random, but valid
    move action """

    SHORT_NAME = "random"

    def __init__(self, board, piece):
        super().__init__()
        self._board = board
        self._maze = board.maze
        self._piece = piece
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
        insert_location = choice(tuple(self._maze.insert_locations))
        insert_rotation = choice([0, 90, 180, 270])
        self._shift_action = (insert_location, insert_rotation)
        self._board.shift(insert_location, insert_rotation)
        piece_location = self._maze.maze_card_location(self._piece.maze_card)
        reachable_locations = Graph(self._maze).reachable_locations(piece_location)
        self._move_action = choice(tuple(reachable_locations))
