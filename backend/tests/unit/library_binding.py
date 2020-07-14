""" This module provides a subclass for the external library call, which computes a series of actions """
from server.model.algorithm.external_library import ExternalLibraryBinding
import server.model.algorithm.util as algo_util


class CompletePathLibraryBinding(ExternalLibraryBinding):
    """ The external libraries only return one action, but the tests require a complete path, i.e. a series of actions
    which reach the objective. The subclass in this module repeatedly calls the library to create such a path.
    It provides the same interface as exhaustive_search.Optimizer, so it can be used as a fixture. """

    def __init__(self, path, board, piece, previous_shift_location=None):
        board = algo_util.copy_board(board, pieces=[piece])
        piece = board.pieces[0]
        board.validate_moves = True
        board.maze.validation = True
        ExternalLibraryBinding.__init__(self, path, board, piece, previous_shift_location)

    def find_optimal_actions(self):
        """ repeatedly calls library to retrieve all actions to reach the objective """
        has_reached = False
        actions = []
        steps = 0
        while not has_reached and steps < 20:
            shift_action, move_location = self.find_optimal_action()
            actions.extend([shift_action, move_location])
            self._board.shift(shift_action[0], shift_action[1])
            has_reached = self._board.move(self._piece, move_location)
            steps = steps + 1
        return actions
