""" The model of the game.

Game is the representation one played game.
It consists of a Board and the Turns.

Board manages the current state of the set of game components currently on the table, i.e.
the Maze, a 2-d array of MazeCards, a leftover MazeCard, and a list of Pieces.

MazeCard represents a single maze card, with outward connections and a rotation.

The Maze is a wrapper for a 2-d array of MazeCards, with convenient functions.

A Piece represents a player, with a unique ID,
a reference to a maze card the piece is currently positioned on and an objective.
BoardLocation is a wrapper for a row and a column. If both are positive, the position is in the maze.
"""
import itertools
from random import choice

from labyrinth.model import exceptions
from labyrinth.model.reachable import Graph
from labyrinth.model.algorithm import out_paths_dict

_HASH_MAX = 31


class BoardLocation:
    """ A board location, defined by the row and the column.
    The location does now know the extent of the maze.
    """

    def __init__(self, row: int, column: int):
        self.row = row
        self.column = column

    def add(self, row_delta: int, column_delta: int):
        """ Returns a new BoardLocation by adding the deltas to the current location """
        return BoardLocation(self.row + row_delta, self.column + column_delta)

    @classmethod
    def copy(cls, board_location):
        """ Create new BoardLocation as a copy from another """
        return cls(board_location.row, board_location.column)

    def __eq__(self, other):
        return isinstance(self, type(other)) and \
            self.column == other.column and \
            self.row == other.row

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return self.row*_HASH_MAX + self.column

    def __str__(self):
        return "({}, {})".format(self.row, self.column)

    def __repr__(self):
        return self.__str__()


class MazeCard:
    """ Represents one maze card
    The out_paths field defines the type of the card.
    It is a string made up of the letters 'N', 'E', 'S', 'W', defining the paths
    going out of this maze card in the directions Up, Right, Down and Left, respectively.
    There are three types of cards, the straight line (NS), the corner(NE) and the T-junction (NES).
    A card also has a rotation in degrees, one of 0, 90, 180, and 270.
    This rotation has to be taken into account when determining the actual outgoing connections.
    Each MazeCard is identified with a unique ID.
    """
    STRAIGHT = "NS"
    CORNER = "NE"
    T_JUNCT = "NES"
    CROSS = "NESW"

    next_id = 0
    _DIRECTIONS_BY_OUT_PATHS_ROTATED = out_paths_dict.dictionary

    def __init__(self, identifier=0, out_paths=STRAIGHT, rotation=0):
        self._out_paths = out_paths
        self._rotation = rotation
        self._id = identifier

    @property
    def identifier(self):
        """ Getter of read-only identifier """
        return self._id

    @property
    def rotation(self):
        """ Getter of rotation """
        return self._rotation

    @rotation.setter
    def rotation(self, value):
        """ Setter of rotation, validates new value """
        if value % 90 != 0:
            raise exceptions.InvalidRotationException("Rotation {} is not divisible by 90".format(value))
        self._rotation = value % 360

    @property
    def out_paths(self):
        """ Getter of read-only out_paths """
        return self._out_paths

    def has_rotated_out_path(self, direction):
        """ Returns whether there is an outgoing path
        in a given direction, taking the rotation into account.

        :param direction: a tuple describing the direction of the path, e.g. (-1, 0) for north
        :return: true iff there is a path in the given direction
        """
        return direction in self._DIRECTIONS_BY_OUT_PATHS_ROTATED[(self._out_paths, self._rotation)]

    def rotated_out_paths(self):
        """ Returns an iteratable over all directions
        with outgoing paths, taking rotation into account.
        """
        return self._DIRECTIONS_BY_OUT_PATHS_ROTATED[(self._out_paths, self._rotation)]

    def __eq__(self, other):
        return isinstance(self, type(other)) and \
            self.identifier == other.identifier

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.identifier))

    def __str__(self):
        return "(MazeCard: identifier: {}, rotation: {}, out_paths: {})".format(self.identifier,
                                                                                self.rotation,
                                                                                self.out_paths)

    def __repr__(self):
        return self.__str__()


class Piece:
    """ Represents a player's piece
    Each piece has a reference to a MazeCard instance as its position.
    """

    def __init__(self, piece_index, maze_card: MazeCard):
        self.piece_index = piece_index
        self.maze_card = maze_card


class Maze:
    """ Represent the state of the maze.
    The state is maintained in a 2-d array of MazeCard instances.
    """

    def __init__(self, maze_size=7, validate_locations=True):
        self._maze_size = maze_size
        self._maze_locations = [BoardLocation(row, column) for row in range(maze_size) for column in range(maze_size)]
        self._maze_cards = [[None for _ in range(maze_size)] for _ in range(maze_size)]
        self.validation = validate_locations

    @property
    def maze_size(self):
        """ Getter for maze_size """
        return self._maze_size

    @property
    def maze_locations(self):
        """ Returns all BoardLocations of this maze """
        return self._maze_locations

    def __getitem__(self, location):
        """ Retrieves the maze card at a given location

        :param location: a BoardLocation instance
        :raises InvalidLocationException: if location is outside of the board
        :return: the MazeCard instance
        """
        if self.validation:
            self._validate_location(location)
        return self._maze_cards[location.row][location.column]

    def __setitem__(self, location, maze_card):
        """ Sets the maze card at a given location

        :param location: a BoardLocation instance
        :raises InvalidLocationException: if location is outside of the board
        :param maze_card: the maze card to set
        """
        if self.validation:
            self._validate_location(location)
        self._maze_cards[location.row][location.column] = maze_card

    def maze_card_location(self, maze_card):
        """ Returns the BoardLocation of the given MazeCard,
        or None if the card is not in the maze """
        for location in self.maze_locations:
            if self[location] == maze_card:
                return location
        return None

    def shift(self, location, inserted_maze_card):
        """ Performs a shifting action on the maze

        :param location: the location of the inserted maze card
        :param inserted_maze_card: the maze card to insert
        :raises InvalidShiftLocationException: for invalid shift location
        :return: the pushed out maze card
        """
        self._validate_shift_location(location)
        direction = self._determine_shift_direction(location)
        shift_line_locations = []
        current_location = location
        while current_location is not None:
            shift_line_locations.append(current_location)
            current_location = self._neighbor(current_location, direction)
        pushed_out = self[shift_line_locations[-1]]
        self._shift_all(shift_line_locations)
        self[shift_line_locations[0]] = inserted_maze_card
        return pushed_out

    def _shift_all(self, shift_locations):
        """ Shifts the maze cards along the given locations """
        for source, target in reversed(list(zip(shift_locations, shift_locations[1:]))):
            self[target] = self[source]

    def _determine_shift_direction(self, shift_location):
        """ Returns the direction to shift to for a given location

        :param shift_location: the location of the pushed in maze card
        :raises InvalidShiftLocationException: if the location is not on the border
        :return: the direction as a tuple
        """
        if shift_location.row == self._maze_size - 1:
            return (-1, 0)
        if shift_location.row == 0:
            return (1, 0)
        if shift_location.column == self._maze_size - 1:
            return (0, -1)
        if shift_location.column == 0:
            return (0, 1)
        raise exceptions.InvalidShiftLocationException(
            "Location {} is not shiftable (not on border)".format(str(shift_location)))

    def _neighbor(self, location, direction):
        """ Determines the neighbor of a location, if possible.

        :param location: the location the neighbor is requested for
        :param direction: a tuple describing the position of the requested neighbor,
        relative to the given location, e.g. (-1, 0) for the northern neighbor
        :return: a new location in the given direction,
        or None, if the location is outside of the maze's extent
        """
        new_location = location.add(*direction)
        if not self.is_inside(new_location):
            new_location = None
        return new_location

    def is_inside(self, location):
        """ Determines if the given location is inside the maze """
        return location.row >= 0 and \
            location.column >= 0 and \
            location.row < self._maze_size and \
            location.column < self._maze_size

    def _validate_location(self, location):
        if not self.is_inside(location):
            raise exceptions.InvalidLocationException("Location {} is outside of the maze.".format(str(location)))

    def _validate_shift_location(self, location):
        if self.validation:
            self._validate_location(location)


class Board:
    """
    The board state of a game of labyrinth, including the maze, the pieces, and the objective
    """
    START_LOCATIONS = None
    OBJECTIVE_LOCATION = None

    def __init__(self, maze=None, leftover_card=None, objective_maze_card=None):
        self._pieces = []
        if not maze:
            maze = Maze()
        self._maze = maze
        self._shift_locations = self._generate_shift_locations()
        if not leftover_card:
            leftover_card = MazeCard()
        self._leftover_card = leftover_card
        if not objective_maze_card:
            objective_maze_card = self._find_new_objective_maze_card()
        self._objective_maze_card = objective_maze_card
        self.validate_moves = True

    @property
    def leftover_card(self):
        """ Getter for leftover card """
        return self._leftover_card

    @property
    def objective_maze_card(self):
        """ Getter for objective maze card """
        return self._objective_maze_card

    @property
    def maze(self):
        """ Getter for maze """
        return self._maze

    @property
    def pieces(self):
        """ Getter for pieces """
        return self._pieces

    @property
    def shift_locations(self):
        """ Getter for shift_locations """
        return self._shift_locations

    def clear_pieces(self):
        """ Removes all pieces currently on the board """
        self._pieces.clear()

    def create_piece(self):
        """ Creates and places a piece on the board.
        Generates new objective, because the old one could be the same as the new piece's starting location. """
        next_index = self._next_free_piece_index()
        start_locations = self._start_locations()
        next_location = start_locations[next_index % len(start_locations)]
        piece = Piece(next_index, self._maze[next_location])
        self._pieces.append(piece)
        self._objective_maze_card = self._find_new_objective_maze_card()
        return piece

    def _start_locations(self):
        if not self.START_LOCATIONS:
            maze_size = self.maze.maze_size
            start_locations = [BoardLocation(0, 0),
                               BoardLocation(0, maze_size - 1),
                               BoardLocation(maze_size - 1, maze_size - 1),
                               BoardLocation(maze_size - 1, 0)]
        else:
            start_locations = self.START_LOCATIONS
        return start_locations

    def _next_free_piece_index(self):
        current_piece_indices = set(map(lambda piece: piece.piece_index, self._pieces))
        next_index = 0
        for try_index in itertools.count():
            if try_index not in current_piece_indices:
                next_index = try_index
                break
        return next_index

    def remove_piece(self, piece):
        """ Removes a piece from the board """
        self._pieces.remove(piece)

    def shift(self, shift_location: BoardLocation, leftover_rotation: int):
        """ Performs a shifting action """
        self._validate_shift_location(shift_location)
        self._leftover_card.rotation = leftover_rotation
        pushed_card = self._leftover_card
        self._leftover_card = self._maze.shift(shift_location, self._leftover_card)
        for card_piece in self._find_pieces_by_maze_card(self._leftover_card):
            card_piece.maze_card = pushed_card

    def move(self, piece, target_location):
        """ Performs a move action. Returns True iff objective was reached. """
        piece_location = self._maze.maze_card_location(piece.maze_card)
        target = self._maze[target_location]
        self._validate_move_location(piece_location, target_location)
        piece.maze_card = target
        if target == self.objective_maze_card:
            self._objective_maze_card = self._find_new_objective_maze_card()
            return True
        return False

    def opposing_border_location(self, border_location):
        """ Returns the location directly opposite of the given location on the border """
        row, column = border_location.row, border_location.column
        limit = self.maze.maze_size - 1
        borders = {0, limit}
        if row in borders:
            return BoardLocation(limit - row, column)
        if column in borders:
            return BoardLocation(row, limit - column)
        raise exceptions.InvalidStateException("Location {} is not on the border".format(border_location))

    def _validate_move_location(self, piece_location, target_location):
        # sourcery skip: merge-nested-ifs
        if self.validate_moves:
            if not Graph(self._maze).is_reachable(piece_location, target_location):
                raise exceptions.MoveUnreachableException("Locations {} and {} are not connected".format(
                    piece_location, target_location))

    def _validate_shift_location(self, location):
        if location not in self._shift_locations:
            raise exceptions.InvalidShiftLocationException(
                "Location {} is not shiftable (fixed maze cards)".format(str(location)))

    def _generate_shift_locations(self):
        maze_size = self.maze.maze_size
        shift_locations = []
        for position in range(1, maze_size, 2):
            shift_locations.append(BoardLocation(0, position))
            shift_locations.append(BoardLocation(position, 0))
            shift_locations.append(BoardLocation(maze_size - 1, position))
            shift_locations.append(BoardLocation(position, maze_size - 1))
        return frozenset(shift_locations)

    def _find_pieces_by_maze_card(self, maze_card):
        """ Finds pieces whose maze_card field matches the given maze card

        :param maze_card: an instance of MazeCard
        """
        return [piece for piece in self._pieces if piece.maze_card is maze_card]

    def _find_new_objective_maze_card(self):
        """ Finds a random maze card not occupied by a player's piece """
        if not self.OBJECTIVE_LOCATION:
            maze_cards = set([self._maze[location]
                              for location in self._maze.maze_locations] + [self._leftover_card])
            for piece in self._pieces:
                maze_cards.discard(piece.maze_card)
            return choice(tuple(maze_cards))
        return self._maze[self.OBJECTIVE_LOCATION]


class Player:
    """ This class represents a player playing a game """

    def __init__(self, identifier=None, game=None, piece=None, board=None):
        self._id = identifier
        self._board = board
        self._piece = piece
        self._game = game
        self.score = 0

    @property
    def piece(self):
        """ Getter for piece """
        return self._piece

    @property
    def identifier(self):
        """ Getter for identifier """
        return self._id

    @property
    def board(self):
        """ Getter for board """
        return self._board

    def set_game(self, game):
        """ Sets the game this player is part of
        Also sets the board and the player's piece """
        self._game = game
        self.set_board(game.board)

    def set_board(self, board: Board):
        """ Setter for board """
        self._board = board
        if not self._piece or self._piece not in board.pieces:
            self._piece = board.create_piece()

    def register_in_turns(self, turns):
        """ registers itself in a Turns manager """
        turns.add_player(self)


class PlayerAction:
    """ This class represent the action of a specific player.
    This class should only be used inside of Turns """

    MOVE_ACTION = "MOVE"
    SHIFT_ACTION = "SHIFT"

    def __init__(self, player, action, turn_callback=None):
        """
        :param player: a Player instance
        :param action: PlayerAction.MOVE_ACTION or PlayerAction.SHIFT_ACTION
        :param turn_callback: a method which is called with no arguments, if it is the player's turn.
        """
        self._player = player
        self._action = action
        self._turn_callback = turn_callback

    @property
    def player(self):
        """ Getter of player """
        return self._player

    @property
    def action(self):
        """ Getter of action """
        return self._action

    @property
    def turn_callback(self):
        """ Getter of turn_callback """
        return self._turn_callback

    def __eq__(self, other):
        return isinstance(self, type(other)) and \
            self.player.identifier == other.player.identifier and \
            self.action == other.action

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.player.identifier, self.action))


class Turns:
    """ This class contains the turn progression.

    It manages player's turns and the correct order of their actions.
    The methods expect two parameters: a player parameter, and an action parameter.
    The former is an instance of Player, the latter is either PlayerAction.MOVE_ACTION or PlayerAction.SHIFT_ACTION
    """

    def __init__(self, players=None, next_action=None):
        self._player_actions = []
        self.init(players)
        self._next = 0
        if next_action:
            self._next = self._player_actions.index(next_action)

    def init(self, players=None):
        """ clears turn progression, adds all players """
        self._player_actions = []
        if players:
            for player in players:
                player.register_in_turns(self)

    def add_player(self, player, turn_callback=None):
        """ Adds a player to the turn progression, if he is not present already """
        already_present = any(
            player_action.player is player
            for player_action in self._player_actions
        )

        if not already_present:
            self._player_actions.append(PlayerAction(player, PlayerAction.SHIFT_ACTION, turn_callback))
            self._player_actions.append(PlayerAction(player, PlayerAction.MOVE_ACTION, turn_callback))

    def remove_player(self, player):
        """ Removes all PlayerActions with this player. If it was this player's turn to play, the next
        Player has to play and is informed if available """
        player_index = self._player_actions.index(PlayerAction(player, PlayerAction.MOVE_ACTION))
        if player_index - 1 <= self._next <= player_index:
            next_player_index = (self._next + 2) % len(self._player_actions)
            next_player = self._player_actions[next_player_index].player
            self._next = self._player_actions.index(PlayerAction(next_player, PlayerAction.SHIFT_ACTION))
            if self.next_player_action().turn_callback:
                self.next_player_action().turn_callback()
        if self._next > player_index:
            self._next -= 2
        self._player_actions = [player_action for player_action in self._player_actions
                                if player_action.player is not player]

    def start(self):
        """ Starts the progression, informs player if necessary """
        self._next = 0
        next_player = self._player_actions[self._next]
        if next_player.turn_callback:
            next_player.turn_callback()

    def is_action_possible(self, player, action):
        """ Checks if the action can be performed by the player

        :param player: an instance of Player
        :param action: one of Turn.MOVE_ACTION and Turn.SHIFT_ACTION
        :return: true, iff the action is to be performed by the player
        """
        return self.next_player_action() == PlayerAction(player, action)

    def perform_action(self, player, action):
        """Method to call when a player performed the given action.
        Checks if it is another player's turn and informs him if that is the case.

        :param player: an instance of Player
        :param action: one of Turn.MOVE_ACTION and Turn.SHIFT_ACTION
        :raises exceptions.TurnActionViolationException: if it is not the player's turn,
        or the player has to perform a different action next.
        """
        if not self.is_action_possible(player, action):
            raise exceptions.TurnActionViolationException("Player {} should not be able to make action {}.".format(
                player.identifier, action))
        self._next = (self._next + 1) % len(self._player_actions)
        player_action = self._player_actions[self._next]
        if player_action.action is PlayerAction.SHIFT_ACTION and player_action.turn_callback:
            player_action.turn_callback()

    def next_player_action(self):
        """ Returns the next PlayerAction in the turn progression """
        try:
            return self._player_actions[self._next]
        except IndexError:
            return None


class Game:
    """ This class represents one played game """
    MAX_PLAYERS = 4

    def __init__(self, identifier, board=None, players=None, turns=None):
        self._id = identifier
        self._players = players if players else []
        self._board = board if board else Board()
        self._turns = turns if turns else Turns()
        self.previous_shift_location = None

    @property
    def turns(self):
        """ Getter for turns """
        return self._turns

    @property
    def board(self):
        """ Getter for board """
        return self._board

    @property
    def players(self):
        """ Getter for players """
        return self._players

    @property
    def identifier(self):
        """ Getter for identifier """
        return self._id

    def next_player_id(self):
        """ Returns an identifier which is currently unused
        to set the id of a new player.
        Throws GameFullException if there are no slots left."""
        if len(self._players) >= self.MAX_PLAYERS:
            raise exceptions.GameFullException("Already {} players playing the game.".format(self.MAX_PLAYERS))
        return max((player.identifier for player in self._players), default=0) + 1

    def add_player(self, player: Player):
        """ Adds a player to the current game, if he is not already one of the current players.
        Throws GameFullException if there are no slots left. """
        if len(self._players) >= self.MAX_PLAYERS:
            raise exceptions.GameFullException("Already {} players playing the game.".format(self.MAX_PLAYERS))
        if any(player.identifier == current_player.identifier for current_player in self._players):
            return
        player.set_game(self)
        player.register_in_turns(self._turns)
        self._players.append(player)

    def get_player(self, player_id):
        """ Finds a player by ID

        :param player_id: an ID of a player
        :return: the Player with the given ID
        :raises PlayerNotFoundException: if no player was found
        """
        try:
            return next(player for player in self._players if player.identifier == player_id)
        except StopIteration:
            raise exceptions.PlayerNotFoundException("No matching player for id {} in this game".format(player_id))

    def remove_player(self, player_id):
        """ Removes player by ID.
        Removes piece from the board, and removes player from turns.

        :param player_id: the ID of the player
        :raises PlayerNotFoundException: if player does not exist
        """
        player = self.get_player(player_id)
        self.board.remove_piece(player.piece)
        self.turns.remove_player(player)
        self.players.remove(player)

    def start_game(self):
        """ Initializes and starts turn progression.
        """
        self._turns.init(self.players)
        self._turns.start()

    def replace_board(self, board):
        """ Replaces the current board with a new one and resets the game.
        For all players, new pieces are created on the board """
        board.pieces.clear()
        for player in self._players:
            player.score = 0
            player.set_board(board)
        self.previous_shift_location = None
        self._board = board
        self._turns.start()

    def shift(self, player_id, new_leftover_location, leftover_rotation):
        """ Performs a shifting action

        :param player_id: the shifting player's ID
        :param new_leftover_location: the new location of the leftover MazeCard
        :param leftover_rotation: the rotation of the leftover MazeCard, in degrees
        (one of 0, 90, 180, 270)
        """
        player = self.get_player(player_id)
        if self._turns.is_action_possible(player, PlayerAction.SHIFT_ACTION):
            self._validate_pushback_rule(new_leftover_location)
            self._board.shift(new_leftover_location, leftover_rotation)
        self.previous_shift_location = new_leftover_location
        self._turns.perform_action(player, PlayerAction.SHIFT_ACTION)

    def move(self, player_id, target_location):
        """ Performs a move action

        :param player_id: the moving player's id
        :param target_location: the board location to move to
        """
        player = self.get_player(player_id)
        if self._turns.is_action_possible(player, PlayerAction.MOVE_ACTION):
            has_reached = self._board.move(player.piece, target_location)
            if has_reached:
                player.score += 1
        self._turns.perform_action(player, PlayerAction.MOVE_ACTION)

    def get_enabled_shift_locations(self):
        """ Returns all currently enabled shift locations.
        These are the shift locations of the board, without the shift location of the previous turn
        """
        opposing_shift_location = None
        if self.previous_shift_location:
            opposing_shift_location = self.board.opposing_border_location(self.previous_shift_location)
        return self.board.shift_locations.difference({opposing_shift_location})

    def _validate_pushback_rule(self, shift_location):
        """ Checks if the requested shift location is different to the shift location of the previous turn
        Throws exception if this rule is violated
        """
        opposing_shift_location = None
        if self.previous_shift_location:
            opposing_shift_location = self.board.opposing_border_location(self.previous_shift_location)
        if shift_location == opposing_shift_location:
            raise exceptions.InvalidShiftLocationException(
                "Location {} is not shiftable (no-pushback rule)".format(str(shift_location)))
