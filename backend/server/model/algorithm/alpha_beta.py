""" This module contains algorithms performing searches on a game tree. """
import math
import operator
from server.model.reachable import RotatableMazeCardGraph, Graph, all_reachables
from server.model.game import Board, MazeCard, BoardLocation
import server.model.algorithm.util as util

class Heuristic:
    """ A heuristic is expected to define a value function. """

    WIN_WEIGHT = 1000

    def value(self, node, current_player):
        """ Heuristic zero-sum value, from viewpoint of player 0.
        
        :param node: the node to evaluate
        :param current_player: the player who made the last move
        :return: a value, and a tuple of value components. The first entry of this tuple should be
        1, if player 0 reaches the objective,
        -1, if player 1 reaches the objective, or
        0, if no player reaches the objective
        """
        board = node.board
        objective_identifier = node.objective_identifier
        win_value = self._win_value(board, objective_identifier, current_player)
        graph = Graph(board.maze)
        reach = [None, None]
        objective_value = [None, None]
        maze_card_value = [0, 0]
        objective_location = util.find_location_by_id(board.maze, objective_identifier)
        for player_index in [0, 1]:
            maze_card = board.pieces[player_index].maze_card
            location = board.maze.maze_card_location(maze_card)
            reach[player_index] = graph.reachable_locations(source=location)
            objective_value[player_index] = self._objective_value(board, location, objective_location)
            if maze_card.out_paths == MazeCard.T_JUNCT:
                maze_card_value[player_index] = 1
        reach_value = len(reach[0]) - len(reach[1])
        reach_value = math.copysign(reach_value**2, reach_value)
        distance_value = objective_value[0] - objective_value[1]
        if win_value != 0:
            distance_value = 0
        maze_card_value = maze_card_value[0] - maze_card_value[1]
        sum_values = win_value * self.WIN_WEIGHT + reach_value * 1 + distance_value * 2 + maze_card_value * 3
        return sum_values, (win_value, reach_value, distance_value, maze_card_value)

    def _win_value(self, board, objective_identifier, player_index):
        """ returns True iff the current player has reached the objective """
        if board.pieces[player_index].maze_card.identifier == objective_identifier:
            return 1 * util.sign(player_index)
        return 0

    def _objective_value(self, board, location, objective_location):
        distance = 15
        if objective_location:
            direct_distance = self._manhattan_distance(location, objective_location)
            if location in board.insert_locations:
                opposite = board.opposing_insert_location(location)
                push_out_distance = self._manhattan_distance(opposite, objective_location)
                if push_out_distance < direct_distance:
                    return -(push_out_distance + 1)
            if direct_distance == 1:
                distance = 4
            elif direct_distance == 2:
                distance = 0
            elif direct_distance == 3:
                distance = 2
            else:
                distance = direct_distance
        return -distance

    def _manhattan_distance(self, one_location, other_location):
        return abs(one_location.row - other_location.row) + abs(one_location.column - other_location.column)


class GameTreeNode:
    """ Represents a node in the game tree for two players.
    Each node represents a shift action and a subsequent move action
    Board instance is expected to have two pieces, which are indexed by 0 and 1, respectively,
    Player 0 is expected to move first (root) """

    def __init__(self, objective_identifier, board=None, parent=None, previous_shift_location=None):
        self.parent = parent
        self.current_shift_action = None
        self.current_move_action = None
        self.previous_shift_location = previous_shift_location
        self.pushed_out_rotation = 0
        self.board = board
        self.objective_identifier = objective_identifier

    @classmethod
    def get_root(cls, board, previous_shift_location=None):
        """ Returns a root to the tree, with parent = None.
        Also sets up the objective identifier. This is necessary, because the objective in board is moved
        after it has been reached (making it impossible to compare the location of piece and objective) """
        board_copy = util.copy_board(board)
        board_copy.validate_moves = False
        root = cls(board.objective_maze_card.identifier, board=board_copy,
                   previous_shift_location=previous_shift_location)
        return root

    def children(self, player_index, sorted_insert_locations=None):
        """ Returns iterable over children of this node """
        piece = self.board.pieces[player_index]
        for insert_location in self._insert_locations(sorted_insert_locations):
            self._do_shift(insert_location, 0)
            piece_location = self.board.maze.maze_card_location(piece.maze_card)
            rotation_depended_locations = self._determine_reachable_locations(piece_location, insert_location)
            for rotation in rotation_depended_locations:
                self._do_rotate(insert_location, rotation)
                for location in rotation_depended_locations[rotation]:
                    self._do_move(piece, piece_location, location)
                    yield GameTreeNode(self.objective_identifier, parent=self, board=self.board,
                                       previous_shift_location=insert_location)
                    self._undo_move(piece)
            self._undo_shift()

    def _insert_locations(self, predefined_order=None):
        if predefined_order is None:
            predefined_order = []
        disabled_shift_location = None
        if self.previous_shift_location:
            disabled_shift_location = self.board.opposing_insert_location(self.previous_shift_location)
        for insert_location in predefined_order:
            if insert_location != disabled_shift_location:
                yield insert_location
        for insert_location in self.board.insert_locations:
            if insert_location not in predefined_order and \
                    insert_location != disabled_shift_location:
                yield insert_location

    def _rotations(self, location):
        rotations = [0, 90, 180, 270]
        maze_card = self.board.maze[location]
        if maze_card.out_paths == maze_card.STRAIGHT:
            rotations = [0, 90]
        if maze_card.out_paths == maze_card.CROSS:
            rotations = [0]
        return rotations

    def _determine_reachable_locations(self, source, rotatable_location):
        """ Returns a dictionary, where keys are the rotations, and values are iterables over BoardLocations
        If objective is reachable, only this one location is returned (but all rotations)
        """
        graph = RotatableMazeCardGraph(self.board.maze, rotatable_location)
        certainly_reachable, reachable_by_rotation = graph.reachable_locations(source)
        result = dict()
        for location in certainly_reachable:
            if self.board.maze[location].identifier == self.objective_identifier:
                for rotation in self._rotations(rotatable_location):
                    result[rotation] = [location]
                return result
        for rotation, locations in reachable_by_rotation.items():
            for location in locations:
                if self.board.maze[location].identifier == self.objective_identifier:
                    result[rotation] = [location]
        if result:
            return result
        for rotation in self._rotations(rotatable_location):
            result[rotation] = all_reachables(certainly_reachable, reachable_by_rotation, rotation)
        return result

    def reset_board(self, player_index):
        """ The children() iterator alters the board state. Call this method to reset the board
        to its original state if iteration is aborted, e.g. returning from a loop """
        piece = self.board.pieces[player_index]
        self._undo_move(piece)
        self._undo_shift()

    def _do_shift(self, insert_location, rotation):
        self.current_shift_action = (insert_location, rotation)
        self.board.shift(insert_location, rotation)
        self.pushed_out_rotation = self.board.leftover_card.rotation

    def _do_rotate(self, insert_location, rotation):
        self.current_shift_action = (insert_location, rotation)
        self.board.maze[insert_location].rotation = rotation

    def _undo_shift(self):
        insert_location, _ = self.current_shift_action
        opposing_insert_location = self.board.opposing_insert_location(insert_location)
        rotation = self.pushed_out_rotation
        self.board.shift(opposing_insert_location, rotation)

    def _do_move(self, piece, source, target):
        self.current_move_action = (source, target)
        self.board.move(piece, target)

    def _undo_move(self, piece):
        source, _ = self.current_move_action
        piece.maze_card = self.board.maze[source]

    def is_winning(self, player_index):
        """ returns True iff the current player has reached the objective """
        return self.board.pieces[player_index].maze_card.identifier == self.objective_identifier

    def is_root(self):
        """ Returns True iff this node is a root, i.e. iff parent is None """
        return not self.parent


def _copy_shift_location(node):
    shift_location, _ = node.current_shift_action
    return BoardLocation.copy(shift_location)


class AlphaBeta:
    """ Recursively searches for the best action in a two-player game,
    up to a given search depth.
    The algorithm employs alpha and beta cuts to prune unnecessary paths.
    The order of the shift locations is chosen based on the values of the previous branch on the same depth.
    This technique is called killer heuristic, and attempts to produce earlier alpha-beta cutoffs.
    The killer heuristic is employed on each depth but the top-most one,
    because there is no previous branch for this one.

    The constructor takes up to four arguments:
    The board to perform the computation on.
    The pieces, a list where the first entry is piece of the player, the second the opponent's piece.
    Optionally, the previous turn's shift location can be passed,
    so that the no-pushback rule can be respected.
    The depth is restricted to 3 by default, and can be set by the depth parameter.
    """

    INF = 100000

    def __init__(self, heuristic=None, depth=3):
        if not heuristic:
            heuristic = Heuristic()
        self._heuristic = heuristic
        self._depth = depth
        self._aborted = False
        self._best_actions = None
        self._shift_locations_per_depth = {}

    def find_actions(self, root):
        """ Finds an action which maximzes the heuristic value.
        This algorithm only returns the best next action, not the entire path.
        
        :param root: an instance of GameTreeNode, the root of the tree to search
        :return: the best actions, the maximin value, and a tuple of components of this value,
        where the first entry signifies if player 0 is certainly loosing (-1), certainly winning (1), or none of both (0)
        """

        self._shift_locations_per_depth = {}
        for depth in range(1, self._depth):
            self._shift_locations_per_depth[depth] = {}
        value, values = self._negamax(node=root, depth=self._depth, alpha=-self.INF, beta=self.INF, player=0)
        return self._best_actions, value, values

    def _negamax(self, node, depth, alpha, beta, player):
        if depth == 0 or node.is_winning(util.other(player)):
            value, values = self._heuristic.value(node, util.other(player))
            return util.sign(player) * value, values
        best_value = -self.INF
        best_values = None
        ordered_shift_locations = self._extract_ordered_shifts(depth)
        for child in node.children(player, ordered_shift_locations):
            value, values = self._negamax(child, depth - 1, -beta, -alpha, util.other(player))
            value = -value
            self._update_shift_values(depth, node, value)
            if value > best_value:
                best_value = value
                best_values = values
                alpha = max(alpha, value)
                if depth == self._depth:
                    self._copy_actions(node)
            if alpha >= beta:
                node.reset_board(player)
                break
            if self._aborted:
                break
        return best_value, best_values

    def _extract_ordered_shifts(self, depth):
        ordered_shift_locations = None
        if depth in range(1, self._depth):
            if self._shift_locations_per_depth[depth]:
                ordered_shift_locations = map(
                    operator.itemgetter(0),
                    sorted(
                        self._shift_locations_per_depth[depth].items(),
                        key=operator.itemgetter(1),
                        reverse=True))
            self._shift_locations_per_depth[depth] = {}
        return ordered_shift_locations

    def _update_shift_values(self, depth, node, value):
        if depth in range(1, self._depth):
            location, _ = node.current_shift_action
            best_location_value = self._shift_locations_per_depth[depth].get(location, -self.INF)
            if value > best_location_value:
                self._shift_locations_per_depth[depth][location] = value

    def _copy_actions(self, node):
        shift_location, rotation = node.current_shift_action
        shift_action = BoardLocation.copy(shift_location), rotation
        _, target = node.current_move_action
        move_action = BoardLocation.copy(target)
        self._best_actions = (shift_action, move_action)

    def abort_algorithm(self):
        """ Sets a flag to abort the algorithm, which is checked regularly. """
        self._aborted = True


class IterativeDeepening:
    """ Iteratively starts a minimax with increasing depths.

    An instance is parameterized with a search technique, e.g. AlphaBeta or Minimax,
    and a heuristic which evaluates nodes. The heuristic is also used to abort the search.
    The search is aborted either by the heuristic, if the current best value represents a certain win or loss,
    or the stop_iterating() method is called """

    def __init__(self, heuristic=None):
        if not heuristic:
            heuristic = Heuristic()
        self._heuristic = heuristic
        self._aborted = False
        self._current_search = None
        self._shift_action = None
        self._move_action = None

    def start_iterating(self, board, pieces, previous_shift_location=None):
        """ Starts iterating """
        depth = 0
        win_detected = False
        while not self._aborted and not win_detected:
            depth = depth + 1
            self._current_search = AlphaBeta(self._heuristic, depth)
            root = GameTreeNode.get_root(util.copy_board(board, pieces),
                                         previous_shift_location=previous_shift_location)
            actions, _, values = self._current_search.find_actions(root)
            win_detected = abs(values[0]) == 1
            if not self._aborted:
                self._shift_action, self._move_action = actions

    def stop_iterating(self):
        """ Stops the currently running iteration """
        self._aborted = True
        self._current_search.abort_algorithm()
