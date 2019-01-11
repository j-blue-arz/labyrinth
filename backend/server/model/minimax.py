""" This module contains algorithms performing searches on a game tree. """
import copy
from .maze_algorithm import Graph, ReachedLocation
from .game import Board, Piece, MazeCard, Maze, BoardLocation


_MAZE_SIZE = 7
# TODO refactor: use location.add, directly create new location instead of update
# TODO make BoardLocation immutable, then no need to return copies


def _setup_shift_correction(shift_location):
    if shift_location.row == 0:
        def constant_part(location): return location.column

        def update_location(location): return _change_row(location, 1)
    elif shift_location.row == _MAZE_SIZE - 1:
        def constant_part(location): return location.column

        def update_location(location): return _change_row(location, -1)
    elif shift_location.column == 0:
        def constant_part(location): return location.row

        def update_location(location): return _change_column(location, 1)
    elif shift_location.column == _MAZE_SIZE - 1:
        def constant_part(location): return location.row

        def update_location(location): return _change_column(location, -1)
    return constant_part, update_location


def _change_row(location, delta):
    location.row = (location.row + delta) % _MAZE_SIZE


def _change_column(location, delta):
    location.column = (location.column + delta) % _MAZE_SIZE


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
    piece_maze_cards = [maze_card_by_id[piece.maze_card.identifier] for piece in board.pieces]
    for maze_card in piece_maze_cards:
        board_copy.pieces.append(Piece(maze_card))
    return board_copy


class GameTreeNode:
    """ Represents a node in the game tree for two players.
    Each node represents a shift action and all maze cards reached for each player.
    Board instance is expected to have two pieces, which are indexed by 0 and 1, respectively,
    Player 0 is expected to move first (root) """

    def __init__(self, parent=None, shift_action=None):
        self.parent = parent
        self.shift_action = shift_action
        self.reached_locations = [[], []]
        if parent:
            self.player_index = 1 - parent.player_index
        else:
            self.player_index = 1
        self.board = None

    @classmethod
    def get_root(cls, board):
        """ Returns a root to the tree, with parent = None """
        root = cls()
        root.board = _copy_board(board)
        root.board.validate_moves = False
        for index, piece in enumerate(root.board.pieces):
            location = root.board.maze.maze_card_location(piece.maze_card)
            root.reached_locations[index] = [ReachedLocation(location, None)]
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
            other_index = 1 - self.player_index
            other_locations = self._get_updated_parent_reached_locations(other_index)
            self.reached_locations[other_index] = \
                    [ReachedLocation(location, location) for location in other_locations]
            player_locations = self._get_updated_parent_reached_locations(self.player_index)
            reachable_locations = \
                    list(Graph(self.board.maze).reachable_locations(sources=player_locations, with_sources=True))
            self.reached_locations[self.player_index] = reachable_locations

    def _get_updated_parent_reached_locations(self, player_index):
        shift_location, _ = self.shift_action
        constant_part, update_location = _setup_shift_correction(shift_location)
        locations = [reached.location for reached in self.parent.reached_locations[player_index]]
        for index, location in enumerate(locations):
            if constant_part(location) == constant_part(shift_location):
                locations[index] = BoardLocation.copy(location)
                update_location(locations[index])
        return locations

    def is_winning(self):
        """ If this node is a shift, returns True iff the objective can be reached
        Returns False if this node is a move. """
        self._compute()
        for reached in self.reached_locations[self.player_index]:
            if self.board.objective_maze_card.identifier == self.board.maze[reached.location].identifier:
                return True
        return False

    def is_root(self):
        """ Returns True iff this node is a root, i.e. iff parent is None """
        return not self.parent

    def _shift_location(self):
        return self.shift_action[0]


class Optimizer:
    """ Recursively searches for the best action in a two-player game,
    up to a given search depth.

    The constructor takes up to three arguments:
    The board to perform the computation on.
    The pieces, a list where the first entry is piece of the player, the second the opponent's piece.
    Optionally, the previous turn's shift location can be passed,
    so that the no-pushback rule can be respected.
    """

    INF = 10
    WIN = 1
    LOSS = -1

    def __init__(self, board, pieces, previous_shift_location=None, depth=3):
        self._board = board
        self._board.clear_pieces()
        self._board.pieces.extend(pieces)
        self._aborted = False
        self._previous_shift_location = previous_shift_location
        self._depth = depth

    def find_optimal_actions(self):
        """ Finds a succession of actions where the opponent does not reach the 
        objective before the player does. If there exists such actions up to d turns, it is found.
        This algorithm only returns the best next action, not the entire path.

        :param depth: the maximum search depth, defaults to 3
        """
        root = GameTreeNode.get_root(self._board)
        value, leaf = self._negamax(node=root, depth=self._depth, player=0)
        return self._actions(leaf), value

    def _actions(self, leaf):
        current = leaf
        move = current.reached_locations[0][0]
        for reached in current.reached_locations[0]:
            if current.board.maze[reached.location].identifier == self._board.objective_maze_card.identifier:
                move = reached
        while not current.parent.is_root():
            move = self._find_location_in_shift_corrected_parent_targets(move.source, current)
            current = current.parent
        return current.shift_action, move.location

    def _find_location_in_shift_corrected_parent_targets(self, location, node):
        shift_location, _ = node.shift_action
        constant_part, update_location = _setup_shift_correction(shift_location)
        for reached in node.parent.reached_locations[0]:
            if constant_part(reached.location) == constant_part(shift_location):
                update_location(reached.location)
            if reached.location == location:
                return reached
        return None

    def _negamax(self, node, depth, player):
        if node.is_winning():
            return 1, node
        if depth == 0:
            return 0, node
        best_value = -self.INF
        best_leaf = None
        for child in node.children():
            value, leaf = self._negamax(child, depth - 1, 1 - player)
            if depth != self._depth:
                value = -value
            if value > best_value:
                best_value = value
                best_leaf = leaf
            if best_value == 1:
                break
        return best_value, best_leaf
