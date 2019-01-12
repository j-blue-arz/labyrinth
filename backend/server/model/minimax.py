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

def _sign(player):
    return 1 - 2*player

def _other(player):
    return 1 - player

def _copy_board(board):
    maze_card_by_id = {}
    leftover_card = MazeCard(board.leftover_card.identifier, board.leftover_card.doors, board.leftover_card.rotation)
    maze_card_by_id[leftover_card.identifier] = leftover_card
    maze = Maze(validate_locations=False)
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
    Each node represents a shift action and a subsequent move action
    Board instance is expected to have two pieces, which are indexed by 0 and 1, respectively,
    Player 0 is expected to move first (root) """

    objective_identifier = 0

    def __init__(self, board=None, parent=None, previous_shift_location=None):
        self.parent = parent
        self.current_shift_action = None
        self.current_move_action = None
        self.previous_shift_location = previous_shift_location
        self.pushed_out_rotation = 0
        if parent:
            self.player_index = 1 - parent.player_index
            self.depth = parent.depth - 1
        else:
            self.depth = None
            self.player_index = 1
        self.board = board

    @classmethod
    def get_root(cls, board, previous_shift_location=None, max_depth=3):
        """ Returns a root to the tree, with parent = None.
        Also sets up the objective identifier. This is necessary, because the objective in board is moved
        after it has been reached (making it impossible to compare the location of piece and objective) """
        board_copy = _copy_board(board)
        board_copy.validate_moves = False
        root = cls(board=board_copy, previous_shift_location=previous_shift_location)
        root.depth = max_depth
        cls.objective_identifier = board.objective_maze_card.identifier
        return root

    def children(self):
        """ Returns iterable over children of this node """
        disabled_shift_location = None
        if self.previous_shift_location:
            disabled_shift_location = self.board.opposing_insert_location(self.previous_shift_location)
        piece = self.board.pieces[_other(self.player_index)]
        for insert_location in self.board.INSERT_LOCATIONS:
            if insert_location != disabled_shift_location:
                for rotation in self._current_rotations(): # TODO simply rotate inserted card
                    self._do_shift(insert_location, rotation)
                    piece_location = self.board.maze.maze_card_location(piece.maze_card)
                    reachable_locations = self._determine_reachable_locations(piece_location)
                    for location in reachable_locations:
                        self._do_move(piece, piece_location, location)
                        yield GameTreeNode(parent=self, board=self.board, previous_shift_location=insert_location)
                        self._undo_move(piece)
                    self._undo_shift()

    def _current_rotations(self):
        rotations = [0, 90, 180, 270]
        leftover_card = self.board.leftover_card
        if leftover_card.doors == leftover_card.STRAIGHT:
            rotations = [0, 90]
        return rotations

    def _determine_reachable_locations(self, source):
        """ If the objective can be reached, return only that one location.
        If depth <= 2, this is the last move made by the current player. Return only one (any) location.
        Else return all reachable locations. """
        reachable_locations = Graph(self.board.maze).reachable_locations(source)
        objective_reachable_location = None
        for reachable_location in reachable_locations:
            if self.board.maze[reachable_location].identifier == self.objective_identifier:
                objective_reachable_location = reachable_location
                break
        if objective_reachable_location:
            reachable_locations = [objective_reachable_location]
        elif self.depth <= 2:
            reachable_locations = [reachable_locations.pop()]
        return reachable_locations


    def reset_board(self):
        """ The children() iterator alters the board state. Call this method to reset the board
        to its original state if iteration is aborted, e.g. returning from a loop """
        piece = self.board.pieces[_other(self.player_index)]
        self._undo_move(piece)
        self._undo_shift()

    def _do_shift(self, insert_location, rotation):
        self.current_shift_action = (insert_location, rotation)
        self.board.shift(insert_location, rotation)
        self.pushed_out_rotation = self.board.leftover_card.rotation

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

    def is_winning(self):
        """ returns True iff the current player has reached the objective """
        return self.board.pieces[self.player_index].maze_card.identifier == self.objective_identifier

    def value(self):
        """ Returns 1 if player 0 is winning, -1 if player 1 is winning, 0 else """
        if self.is_winning():
            return 1
        return 0

    def is_root(self):
        """ Returns True iff this node is a root, i.e. iff parent is None """
        return not self.parent


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
        self._board = _copy_board(board)
        self._board.clear_pieces()
        self._board.pieces.extend(pieces)
        self._aborted = False
        self._previous_shift_location = previous_shift_location
        self._depth = depth
        self._best_actions = None

    def find_optimal_actions(self):
        """ Finds a succession of actions where the opponent does not reach the
        objective before the player does. If there exists such actions up to d turns, it is found.
        This algorithm only returns the best next action, not the entire path.

        :param depth: the maximum search depth, defaults to 3
        """
        root = GameTreeNode.get_root(self._board, max_depth=self._depth)
        value = -self._negamax(node=root, depth=self._depth)
        return self._best_actions, value

    def _negamax(self, node, depth):
        if depth == 0 or node.is_winning():
            return node.value()
        best_value = -self.INF
        for child in node.children():
            value = self._negamax(child, depth - 1)
            if value > best_value:
                best_value = value
                if depth == self._depth:
                    self._copy_actions(node)
            if best_value == 1:
                node.reset_board()
                break
        return -best_value

    def _copy_actions(self, node):
        shift_location, rotation = node.current_shift_action
        shift_action = BoardLocation.copy(shift_location), rotation
        source, target = node.current_move_action
        move_action = BoardLocation.copy(target)
        self._best_actions = (shift_action, move_action)

