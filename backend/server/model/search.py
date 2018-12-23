""" This module contains algorithms performing searches on a game tree. """
import copy
from .maze_algorithm import Graph


class GameTreeNode:
    """ Board instance is expected to only have one piece """

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

    @classmethod
    def get_root(cls, board):
        root = cls()
        root.board = copy.deepcopy(board)
        root.board.validate_moves = False
        return root

    def children(self):
        self._compute()
        if self.move_location or self.is_root():
            for insert_location in self.board.maze.insert_locations:
                for rotation in [0, 90, 180, 270]:
                    yield GameTreeNode(parent=self, shift_action=(insert_location, rotation), move_location=None)
        elif self.shift_action:
            piece = self.board.pieces[0]
            piece_location = self.board.maze.maze_card_location(piece.maze_card)
            for move_location in Graph(self.board.maze).reachable_locations(piece_location):
                yield GameTreeNode(self, None, move_location)
        return []

    def _compute(self):
        if not self.board:
            self.board = copy.deepcopy(self.parent.board)
            if self.move_location:
                piece = self.board.pieces[0]
                self.board.move(piece, self.move_location)
            elif self.shift_action:
                shift_location, shift_rotation = self.shift_action
                self.board.shift(shift_location, shift_rotation)

    def is_winning(self):
        if self.shift_action:
            self._compute()
            piece = self.board.pieces[0]
            piece_location = self.board.maze.maze_card_location(piece.maze_card)
            reachable_locations = Graph(self.board.maze).reachable_locations(piece_location)
            for location in reachable_locations:
                if self.board.maze[location] == self.board.objective_maze_card:
                    self.move_location = location
                    return True
        return False

    def is_root(self):
        return not self.parent


class Optimizer:
    def __init__(self, board, piece):
        self._board = board
        self._board.clear_pieces()
        self._board.pieces.append(piece)

    def find_optimal_move(self):
        root = GameTreeNode.get_root(self._board)
        winning_node = _search_winning_node(root)
        return _first_branching_actions(winning_node)


def _first_branching_actions(node):
    if node.parent.is_root():
        return node.shift_action, node.move_location, node.depth
    move_node = node.parent
    shift_node = move_node.parent
    while not shift_node.parent.is_root():
        shift_node, move_node = shift_node.parent.parent, move_node.parent.parent
    return shift_node.shift_action, move_node.move_location, shift_node.depth


def _search_winning_node(root):
    current_layer = [root]
    next_layer = []
    while current_layer:
        for node in current_layer:
            for child in node.children():
                if child.is_winning():
                    child.is_winning()
                    return child
                next_layer.append(child)
        current_layer, next_layer = next_layer, []
