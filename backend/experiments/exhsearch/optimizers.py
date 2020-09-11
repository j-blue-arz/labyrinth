import labyrinth.model.algorithm.external_library as libexhsearch
import labyrinth.model.algorithm.util as algo_util


class CompletePathLibraryBinding(libexhsearch.ExternalLibraryBinding):
    """ The external libraries only return one action, but the tests require a complete path, i.e. a series of actions
    which reach the objective. This subclass repeatedly calls the library to create such a path."""

    def __init__(self, path, board, previous_shift_location=None):
        board = algo_util.copy_board(board)
        piece = board.pieces[0]
        board.validate_moves = True
        board.maze.validation = True
        libexhsearch.ExternalLibraryBinding.__init__(self, path, board, piece, previous_shift_location)

    def find_optimal_actions(self):
        """ repeatedly calls library to retrieve all actions to reach the objective """
        has_reached = False
        actions = []
        steps = 0
        while not has_reached and steps < 20:
            shift_action, move_location = self.find_optimal_action()
            actions.extend([shift_action, move_location])
            self._board.shift(shift_action[0], shift_action[1])
            self._previous_shift_location = shift_action[0]
            has_reached = self._board.move(self._piece, move_location)
            steps += 1
        return actions
