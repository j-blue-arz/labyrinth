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
from .exceptions import LabyrinthDomainException
from .factories import maze_to_string
import server.model.exhaustive_search as exh
import server.model.minimax as mm
import server.model.minimax_heuristic as heuristic


class ComputerPlayer(Player, Thread):
    """ This class represents a computer player. It is instantiated with
    an algorithm_name parameter, either 'random', 'exhaustive-single', or 'minimax'. Default is 'exhaustive-single'.
    A second required parameter is a supplier for the shift and move API URLs.
    This supplier is expected to have methods get_shift_url(game_id, player_id), and
    get_move_url(game_id, player_id).

    If the player is requested to make its action, it starts a thread for time keeping,
    and a thread for letting the algorithm compute the next shift and move action. """

    _SECONDS_TO_ANSWER = 1.5

    def __init__(self, algorithm_name=None, url_supplier=None, move_url=None, shift_url=None, **kwargs):
        Player.__init__(self, **kwargs)
        Thread.__init__(self)
        algorithms = [RandomActionsAlgorithm, ExhaustiveSearchAlgorithm, MinimaxAlgorithm, MinimaxHeuristicAlgorithm]
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
        algorithm = self.algorithm(board, piece, self._game)
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

        #self._validate(shift_action, move_action)
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

    def _post_shift(self, insert_location, insert_rotation):
        dto = server.mapper.api.shift_action_to_dto(insert_location, insert_rotation)
        requests.post(self.shift_url, json=dto)

    def _post_move(self, move_location):
        dto = server.mapper.api.move_action_to_dto(move_location)
        requests.post(self.move_url, json=dto)

    def _find_equal_piece(self, board):
        return next(piece for piece in board.pieces if piece.maze_card.identifier == self._piece.maze_card.identifier)

    def _validate(self, shift_action, move_action):
        board = copy.deepcopy(self._board)
        piece = self._find_equal_piece(board)
        insert_location, rotation = shift_action
        maze_string = maze_to_string(board.maze)
        piece_locations = [board.maze.maze_card_location(piece.maze_card) for piece in board.pieces]
        self_location = board.maze.maze_card_location(piece.maze_card)
        objective_location = board.maze.maze_card_location(board.objective_maze_card)
        try:
            self._game._validate_pushback_rule(insert_location)
            board.shift(insert_location, rotation)
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

    def __init__(self, board, piece, game):
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
        insert_location = choice(tuple(self._enabled_shift_locations))
        insert_rotation = choice([0, 90, 180, 270])
        self._shift_action = (insert_location, insert_rotation)
        self._board.shift(insert_location, insert_rotation)
        piece_location = self._maze.maze_card_location(self._piece.maze_card)
        reachable_locations = Graph(self._maze).reachable_locations(piece_location)
        self._move_action = choice(tuple(reachable_locations))


class ExhaustiveSearchAlgorithm(Thread, exh.Optimizer):
    """ Uses an exhaustive search to compute best single-player solution to objective.
    abort_search() is already implemented in superclass, exh.Optimizer. """
    SHORT_NAME = "exhaustive-single"
    SECONDS_TO_COMPUTE = 1.5

    def __init__(self, board, piece, game):
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

    def __init__(self, board, player_piece, game):
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


class MinimaxHeuristicAlgorithm(Thread, heuristic.IterativeDeepening):
    """ Uses the minimax algorithm to determine an action in a two-player game. """
    SHORT_NAME = "minimax-heuristic"
    SECONDS_TO_COMPUTE = 2.5

    def __init__(self, board, player_piece, game):
        other_piece = next(piece for piece in board.pieces if piece is not player_piece)
        pieces = [player_piece, other_piece]
        heuristic.IterativeDeepening.__init__(self, board, pieces, game.previous_shift_location)
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