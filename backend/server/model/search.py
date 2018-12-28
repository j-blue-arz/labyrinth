""" This module contains algorithms performing searches on a game tree. """
import copy
from .maze_algorithm import Graph


class GameTreeNode:
    """ Represents a node in the game tree. Each shift and move action is a node on its own.
    Board instance is expected to only have one piece """

    def __init__(self, parent=None, shift_action=None, move_location=None):
        self.parent = parent
        self.shift_action = shift_action
        self.move_location = move_location
        if parent:
            if move_location:
                self.depth = parent.depth + 1
            else:
                self.depth = parent.depth
        else:
            self.depth = 0
        self.board = None
        self._reachable_locations = []

    @classmethod
    def get_root(cls, board):
        """ Returns a root to the tree, with parent = None """
        root = cls()
        root.board = copy.deepcopy(board)
        root.board.validate_moves = False
        return root

    def children(self):
        """ Returns iterable over children of this node """
        self._compute()
        if self.move_location or self.is_root():
            for insert_location in self.board.maze.insert_locations:
                for rotation in self._current_rotations():
                    yield GameTreeNode(parent=self, shift_action=(insert_location, rotation), move_location=None)
        elif self.shift_action:
            for move_location in self._reachable_locations:
                yield GameTreeNode(self, None, move_location)
        return []

    def _current_rotations(self):
        rotations = [0, 90, 180, 270]
        leftover_card = self.board.leftover_card
        if leftover_card.doors == leftover_card.STRAIGHT:
            rotations = [0, 90]
        return rotations

    def _compute(self):
        if not self.board:
            self.board = copy.deepcopy(self.parent.board)
            if self.move_location:
                piece = self.board.pieces[0]
                self.board.move(piece, self.move_location)
            elif self.shift_action:
                shift_location, shift_rotation = self.shift_action
                self.board.shift(shift_location, shift_rotation)
                piece = self.board.pieces[0]
                piece_location = self.board.maze.maze_card_location(piece.maze_card)
                self._reachable_locations = Graph(self.board.maze).reachable_locations(piece_location)

    def is_winning(self):
        """ If this node is a shift, returns True iff the objective can be reached
        Returns False if this node is a move. """
        if self.shift_action:
            self._compute()
            for location in self._reachable_locations:
                if self.board.maze[location] == self.board.objective_maze_card:
                    self.move_location = location
                    return True
        return False

    def is_root(self):
        """ Returns True iff this node is a root, i.e. iff parent is None """
        return not self.parent


class Optimizer:
    """ Searches for a winning node in the game tree. """
    def __init__(self, board, piece):
        self._board = board
        self._board.clear_pieces()
        self._board.pieces.append(piece)
        self._aborted = False

    def find_optimal_actions(self):
        """ Finds the optimal succession of actions which reaches the objective.
        Runs until it has found a solution, or abort_search() was called.
        In the former case, returns the solution as a list,
        where each even entry represents a shift action and is a tuple of the form (insert_location, rotation),
        and each odd entry represents a move location.
        Returns None if the search was aborted. """
        root = GameTreeNode.get_root(self._board)
        winning_node = self._search_winning_node(root)
        if winning_node:
            return self._actions(winning_node)
        return None

    def abort_search(self):
        """ Aborts the search """
        self._aborted = True

    def _actions(self, node):
        actions = []
        while not node.is_root():
            if node.move_location:
                actions.append(node.move_location)
            if node.shift_action:
                actions.append(node.shift_action)
            node = node.parent
        actions.reverse()
        return actions


    def _search_winning_node(self, root):
        current_layer = [root]
        next_layer = []
        while current_layer:
            for node in current_layer:
                if self._aborted:
                    return None
                for child in node.children():
                    if child.is_winning():
                        child.is_winning()
                        return child
                    next_layer.append(child)
            current_layer, next_layer = next_layer, []
