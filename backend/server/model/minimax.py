""" This module contains algorithms performing searches on a game tree. """
from .maze_algorithm import RotatableMazeCardGraph
from .game import Board, Piece, MazeCard, Maze, BoardLocation


_MAZE_SIZE = 7

def _other(player):
    return 1 - player

def _copy_board(board, pieces=None):
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
    if not pieces:
        pieces = board.pieces
    piece_maze_cards = [maze_card_by_id[piece.maze_card.identifier] for piece in pieces]
    for maze_card in piece_maze_cards:
        board_copy.pieces.append(Piece(maze_card))
    return board_copy

def _union(dict_of_items, key, items):
    if key in dict_of_items:
        return dict_of_items[key].union(items)
    return items

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
                self._do_shift(insert_location, 0)
                piece_location = self.board.maze.maze_card_location(piece.maze_card)
                rotation_depended_locations = self._determine_reachable_locations(piece_location, insert_location)
                for rotation in rotation_depended_locations:
                    self._do_rotate(insert_location, rotation)
                    for location in rotation_depended_locations[rotation]:
                        self._do_move(piece, piece_location, location)
                        yield GameTreeNode(parent=self, board=self.board, previous_shift_location=insert_location)
                        self._undo_move(piece)
                self._undo_shift()

    def _rotations(self, location):
        rotations = [0, 90, 180, 270]
        maze_card = self.board.maze[location]
        if maze_card.doors == maze_card.STRAIGHT:
            rotations = [0, 90]
        return rotations

    def _determine_reachable_locations(self, source, rotatable_location):
        """ If the objective can be reached for any rotation, return only that one rotation and location.
        If depth <= 2, this is the last move made by the current player. Return only one (any) location.
        if depth == 1, also return only one rotation
        Else return all reachable locations. 
        Returns a dictionary, where keys are the rotations, and values are iterables over BoardLocations
        """
        graph = RotatableMazeCardGraph(self.board.maze, rotatable_location)
        reachable, reachable_map = graph.reachable_locations(source)
        for location in reachable:
            if self.board.maze[location].identifier == self.objective_identifier:
                return {0: [location]}
        for rotation, locations in reachable_map.items():
            for location in locations:
                if self.board.maze[location].identifier == self.objective_identifier:
                    return {rotation: [location]}
        if self.depth >= 3:
            result = dict()
            for rotation in self._rotations(rotatable_location):
                result[rotation] = _union(reachable_map, rotation, reachable)
            return result
        if self.depth == 2:
            result = dict()
            for rotation in self._rotations(rotatable_location):
                if rotation in reachable_map:
                    result[rotation] = [next(iter(reachable_map[rotation]))]
                else:
                    result[rotation] = [next(iter(reachable))]
            return result
        if self.depth == 1:
            if reachable_map:
                available_rotation = next(iter(reachable_map))
                return {available_rotation: [next(iter(reachable_map[available_rotation]))]}
            return {0: [next(iter(reachable))]}


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


class Minimax:
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
        self._board = _copy_board(board, pieces)
        self._aborted = False
        self._previous_shift_location = previous_shift_location
        self._depth = depth
        self._best_actions = None

    def find_actions(self):
        """ Finds a succession of actions where the opponent does not reach the
        objective before the player does. If there exists such actions up to d turns, it is found.
        This algorithm only returns the best next action, not the entire path.

        :param depth: the maximum search depth, defaults to 3
        """
        root = GameTreeNode.get_root(self._board, max_depth=self._depth,
                                     previous_shift_location=self._previous_shift_location)
        value = -self._negamax(node=root, depth=self._depth)
        return self._best_actions, value

    def _negamax(self, node, depth):
        if depth == 0 or node.is_winning():
            return node.value()
        best_value = -self.INF
        for child in node.children():
            value = self._negamax(child, depth - 1)
            if self._aborted:
                break
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
        _, target = node.current_move_action
        move_action = BoardLocation.copy(target)
        self._best_actions = (shift_action, move_action)

    def abort_algorithm(self):
        """ Sets a flag to abort the algorithm, which is checked regularly. """
        self._aborted = True


class IterativeDeepening:
    """ Iteratively starts a minimax with increasing depths. The search is aborted in two ways:
    either the algorithm returns a certain win or loss (of reaching the objective first), or
    the stop_iterating() method is called """

    def __init__(self, board, pieces, previous_shift_location=None):
        self._board = board
        self._pieces = pieces
        self._previous_shift_location = previous_shift_location
        self._aborted = False
        self._current_minimax = None
        self._shift_action = None
        self._move_action = None

    def start_iterating(self):
        """ Starts iterating """
        depth = 0
        value = 0
        while not self._aborted and abs(value) != 1:
            depth = depth + 1
            self._current_minimax = Minimax(self._board, self._pieces, self._previous_shift_location, depth)
            actions, value = self._current_minimax.find_actions()
            if not self._aborted:
                self._shift_action, self._move_action = actions

    def stop_iterating(self):
        """ Stops the currently running iteration """
        self._aborted = True
        self._current_minimax.abort_algorithm()
