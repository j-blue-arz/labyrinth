""" This module contains algorithms performing searches on a game tree. """
import copy
from .maze_algorithm import Graph
from .game import Board, Piece, MazeCard, Maze


class ReachedMazeCard:
    """ Container type for a maze card reached on the path from the start location to the objective.
    It is a container of the identifier of the reached card, its location at the time it was reached,
    and the container it was reached from.
    The ReachedMazeCard container form a tree, parallel to the game tree:
    Each node in the game tree holds a set of these reached maze cards. The from_reached_maze_card member
    of an entry in this set holds an instance of the set in the parent node.
    """
    def __init__(self, maze_card_id, location, from_reached_maze_card):
        self.maze_card_id = maze_card_id
        self.location = location
        self.from_reached_maze_card = from_reached_maze_card

def _copy_board(board):
    maze_card_by_id = {}
    leftover_card = MazeCard(board.leftover_card.identifier, board.leftover_card.doors, board.leftover_card.rotation)
    maze_card_by_id[leftover_card.identifier] = leftover_card
    maze = Maze(validation=False)
    for location in board.maze.maze_locations():
        old_maze_card = board.maze[location]
        maze_card = MazeCard(old_maze_card.identifier, old_maze_card.doors, old_maze_card.rotation)
        maze_card_by_id[maze_card.identifier] = maze_card
        maze[location] = maze_card
    objective = maze_card_by_id[board.objective_maze_card.identifier]
    board_copy = Board(maze, leftover_card, objective)
    board_copy.validate_moves = False
    piece_maze_card = maze_card_by_id[board.pieces[0].maze_card.identifier]
    board_copy.pieces.append(Piece(piece_maze_card))
    return board_copy

class GameTreeNode:
    """ Represents a node in the game tree. Each shift and move action is a node on its own.
    Board instance is expected to only have one piece """

    def __init__(self, parent=None, shift_action=None):
        self.parent = parent
        self.shift_action = shift_action
        self.reached_maze_cards = []
        if parent:
            self.depth = parent.depth + 1
        else:
            self.depth = 0
        self.board = None


    @classmethod
    def get_root(cls, board):
        """ Returns a root to the tree, with parent = None """
        root = cls()
        root.board = _copy_board(board)
        root.board.validate_moves = False
        piece = root.board.pieces[0]
        location = root.board.maze.maze_card_location(piece.maze_card)
        root.reached_maze_cards = [ReachedMazeCard(piece.maze_card.identifier, location, None)]
        return root

    def children(self):
        """ Returns iterable over children of this node """
        self._compute()
        disabled_shift_location = None
        if self.shift_action:
            previous_shift_location, _ = self.shift_action
            disabled_shift_location = self.board.opposing_insert_location(previous_shift_location)
        for insert_location in self.board.INSERT_LOCATIONS:
            if insert_location != disabled_shift_location:
                for rotation in self._current_rotations():
                    yield GameTreeNode(parent=self, shift_action=(insert_location, rotation))
        return []

    def _current_rotations(self):
        rotations = [0, 90, 180, 270]
        leftover_card = self.board.leftover_card
        if leftover_card.doors == leftover_card.STRAIGHT:
            rotations = [0, 90]
        return rotations

    def _compute(self):
        if not self.board:
            self.board = _copy_board(self.parent.board)
            shift_location, shift_rotation = self.shift_action
            self.board.shift(shift_location, shift_rotation)
            piece_locations = [self._location_by_id(reached.maze_card_id) for reached in self.parent.reached_maze_cards]
            reachable_locations = Graph(self.board.maze).reachable_locations(sources=piece_locations, with_sources=True)
            self.reached_maze_cards = list(map(self._reached_maze_card_from_reached_location, reachable_locations))

    def _location_by_id(self, maze_card_id):
        for location in self.board.maze.maze_locations():
            if self.board.maze[location].identifier == maze_card_id:
                return location
        if self.board.leftover_card.identifier == maze_card_id:
            return self._shift_location()
        return None

    def _reached_maze_card_from_reached_location(self, reached_location):
        identifier = self.board.maze[reached_location.location].identifier
        parent_identifier = self.board.maze[reached_location.source].identifier
        parent_reached_card = self._search_reached_in_parent(parent_identifier)
        if parent_reached_card is None and reached_location.source == self._shift_location():
            parent_reached_card = self._search_reached_in_parent(self.board.leftover_card.identifier)
        return ReachedMazeCard(identifier, reached_location.location, parent_reached_card)

    def _search_reached_in_parent(self, maze_card_id):
        return next((reached_card for reached_card in self.parent.reached_maze_cards
                     if reached_card.maze_card_id == maze_card_id), None)

    def is_winning(self):
        """ If this node is a shift, returns True iff the objective can be reached
        Returns False if this node is a move. """
        self._compute()
        for reached in self.reached_maze_cards:
            if self.board.objective_maze_card.identifier == reached.maze_card_id:
                return True
        return False

    def is_root(self):
        """ Returns True iff this node is a root, i.e. iff parent is None """
        return not self.parent

    def _shift_location(self):
        return self.shift_action[0]

class Optimizer:
    """ Searches for a winning node in the game tree. """

    def __init__(self, board, piece, previous_shift_location=None):
        self._board = board
        self._board.clear_pieces()
        self._board.pieces.append(piece)
        self._aborted = False
        self._previous_shift_location = previous_shift_location

    def find_optimal_actions(self):
        """ Finds the optimal succession of actions which reaches the objective.
        Runs until it has found a solution, or abort_search() was called.
        In the former case, returns the solution as a list,
        where each even entry represents a shift action and is a tuple of the form (insert_location, rotation),
        and each odd entry represents a move location.
        Returns None if the search was aborted. """
        root = GameTreeNode.get_root(self._board)
        if self._previous_shift_location:
            root.shift_action = (self._previous_shift_location, 0)
        winning_node = self._search_winning_node(root)
        if winning_node:
            return self._actions(winning_node)
        return None

    def abort_search(self):
        """ Aborts the search """
        self._aborted = True

    def _actions(self, node):
        actions = []
        reached_maze_card = next(reached for reached in node.reached_maze_cards
                                 if reached.maze_card_id == self._board.objective_maze_card.identifier)
        current = node
        while not current.is_root():
            actions.append(reached_maze_card.location)
            actions.append(current.shift_action)
            current = current.parent
            reached_maze_card = reached_maze_card.from_reached_maze_card
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
                        return child
                    next_layer.append(child)
            current_layer, next_layer = next_layer, []
