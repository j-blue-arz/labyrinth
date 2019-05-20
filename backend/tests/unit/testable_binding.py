""" This module provides a subclass for the external library call, which computes a series of actions """
from server.model.algorithm.binding import ExternalLibraryBinding

class TestableLibraryBinding(ExternalLibraryBinding):
    """ The external libraries only return one action, but the tests require a complete path, i.e. a series of actions
    which reach the objective. The subclass in this module repeatedly calls the library to create such a path """

    def __init__(self, path, board, piece, previous_shift_location=None):
        board.validate_moves = True
        board.maze.validation = True
        ExternalLibraryBinding.__init__(self, path, board, piece, previous_shift_location)

    def find_actions(self):
        """ repeatedly calls library to retrieve all actions to reach the objective """
        has_reached = False
        actions = []
        while not has_reached:
            shift_action, move_location = self.find_optimal_action()
            actions.append(shift_action, move_location)
            self._board.shift(shift_action[0], shift_action[1])
            has_reached = self._board.move(self._piece, move_location)
        return actions
