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
from threading import Thread
import time
import random
from datetime import timedelta

from labyrinth.model import exceptions
from labyrinth.model import out_paths_dict
from labyrinth.model.reachable import Graph


class BoardLocation:
    """ A board location, defined by the row and the column.
    The location does now know the extent of the maze.
    """

    _HASH_MAX = 31

    def __init__(self, row: int, column: int):
        self.row = row
        self.column = column

    def add(self, row_delta: int, column_delta: int):
        """ Returns a new BoardLocation by adding the deltas to the current location """
        return BoardLocation(self.row + row_delta, self.column + column_delta)

    def __eq__(self, other):
        return isinstance(self, type(other)) and \
            self.column == other.column and \
            self.row == other.row

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return self.row*self._HASH_MAX + self.column

    def __str__(self):
        return f"({self.row}, {self.column})"

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
        """ Returns an iterable over all directions
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

    A piece is defined by its piece index (in [0..3]), which defines the starting position.
    Each piece has a reference to a MazeCard instance as its current board position.
    """

    def __init__(self, piece_index, maze_card: MazeCard):
        self.piece_index = piece_index
        self.maze_card = maze_card


class Maze:
    """ Represent the state of the maze.
    The state is maintained in a 2-d array of MazeCard instances.
    """

    def __init__(self, maze_size=7):
        self._maze_size = maze_size
        self._maze_locations = [BoardLocation(row, column) for row in range(maze_size) for column in range(maze_size)]
        self._maze_cards = [[None for _ in range(maze_size)] for _ in range(maze_size)]

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
        self._validate_location(location)
        return self._maze_cards[location.row][location.column]

    def __setitem__(self, location, maze_card):
        """ Sets the maze card at a given location

        :param location: a BoardLocation instance
        :raises InvalidLocationException: if location is outside of the board
        :param maze_card: the maze card to set
        """
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
        self._validate_location(location)


class Board:
    """
    The board state of a game of labyrinth, including the maze, the pieces, and the objective
    """
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
        piece_index = self._next_free_piece_index()
        piece = Piece(piece_index, None)
        self.add_piece(piece)
        return piece

    def add_piece(self, piece):
        """ Adds an existing piece to the board, on a start location """
        assert piece not in self._pieces
        self._place_piece_start_location(piece)
        self._pieces.append(piece)

    def _place_piece_start_location(self, piece):
        piece_index = piece.piece_index
        start_locations = self._start_locations()
        start_location = start_locations[piece_index % len(start_locations)]
        piece.maze_card = self._maze[start_location]

    def _start_locations(self):
        maze_size = self.maze.maze_size
        return [BoardLocation(0, 0),
                BoardLocation(0, maze_size - 1),
                BoardLocation(maze_size - 1, maze_size - 1),
                BoardLocation(maze_size - 1, 0)]

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
        start_locations = self._start_locations()
        possible_locations = [location for location in self._maze.maze_locations if location not in start_locations]
        maze_cards = set([self._maze[location]
                          for location in possible_locations] + [self._leftover_card])
        for piece in self._pieces:
            maze_cards.discard(piece.maze_card)
        return random.choice(tuple(maze_cards))


class Player:
    """ This class represents a player playing a game

    Invariants: Board and Game are either both set or both None.
    If both are set, piece is set as well. """

    def __init__(self, identifier, game=None, piece=None, player_name=None):
        """ board and game can only be set together. """
        self._id = identifier
        self._piece = piece
        self._board = None
        self._game = None
        if game:
            self.set_game(game)
        self.score = 0
        self.player_name = player_name

    @property
    def piece(self):
        """ Getter for piece """
        return self._piece

    @property
    def identifier(self):
        """ Getter for identifier """
        return self._id

    def set_game(self, game):
        """ Sets the game this player is part of
        Also sets the board and the player's piece """
        assert not self._game and not self._board
        self._game = game
        self._set_board(game.board)

    def _set_board(self, board: Board):
        self._board = board
        if not self._piece:
            self._piece = board.create_piece()
        assert self._piece in self._board.pieces

    def reset_board(self, board: Board):
        self._board = board
        if self._piece not in board.pieces:
            self._board.add_piece(self._piece)

    def register_in_turns(self, turns):
        """ registers itself in a Turns manager """
        turns.add_player(self)

    def __eq__(self, other):
        return self.identifier == other.identifier

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.identifier)


class PlayerAction:
    """ This class represent the action of a specific player.
    This class should only be used inside of Turns """

    MOVE_ACTION = "MOVE"
    SHIFT_ACTION = "SHIFT"
    PREPARE_SHIFT = "PREPARE_SHIFT"
    PREPARE_MOVE = "PREPARE_MOVE"

    def __init__(self, player, action, turn_callback=None):
        """
        :param player: a Player instance
        :param action: one of PlayerAction.MOVE_ACTION, SHIFT_ACTION, PREPARE_SHIFT, or PREPARE_MOVE
        :param turn_callback: a method which is called if it is the player's turn.
                the method will be called with the required action.
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

    def is_prepare(self):
        return self.action in [self.PREPARE_SHIFT, self.PREPARE_MOVE]

    def copy_with_prepare(self):
        action = self.action if self.is_prepare() else f"PREPARE_{self.action}"
        return PlayerAction(self._player, action)

    def __eq__(self, other):
        return isinstance(self, type(other)) and \
            self.player.identifier == other.player.identifier and \
            self.action == other.action

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.player.identifier, self.action))

    def __str__(self):
        return f"(player {self.player.identifier}, {self.action})"

    def __repr__(self):
        return self.__str__()


class Turns:
    """ This class contains the turn progression.

    It manages player's turns and the correct order of their actions.
    """

    def __init__(self, prepare_delay=timedelta(0), players=None, next_action=None):
        self._turn_changed_listeners = []
        self._turn_states = []
        self._prepare_delay = prepare_delay
        self.init(players)
        self._next = self._turn_states.index(next_action) if next_action else 0
        if self._next_action_is_prepare() and not self._prepare_delay:
            self._next += 1

    def init(self, players=None):
        """ clears turn progression, adds all players """
        self._turn_states = []
        if players:
            for player in players:
                player.register_in_turns(self)

    def _num_players(self):
        return len(self._turn_states) // 4

    def add_player(self, player, turn_callback=None):
        """ Adds a player to the turn progression, if he is not present already """
        already_present = any(
            player_action.player == player
            for player_action in self._turn_states
        )
        if not already_present:
            self._turn_states.append(PlayerAction(player, PlayerAction.PREPARE_SHIFT, turn_callback))
            self._turn_states.append(PlayerAction(player, PlayerAction.SHIFT_ACTION, turn_callback))
            self._turn_states.append(PlayerAction(player, PlayerAction.PREPARE_MOVE, turn_callback))
            self._turn_states.append(PlayerAction(player, PlayerAction.MOVE_ACTION, turn_callback))

    def remove_player(self, player_to_remove):
        """ Removes all PlayerActions with this player. If it was this player's turn to play, the next
        Player has to play and listeners have to be notified. """
        def next_player(state_list):
            next_player_index = (self._next + 4) % len(state_list)
            return state_list[next_player_index].player

        old_next_player_action = self.next_player_action()
        old_player_actions = self._turn_states
        self._turn_states = [player_action for player_action in self._turn_states
                             if player_action.player != player_to_remove]
        if self._turn_states:
            if old_next_player_action.player == player_to_remove:
                new_next_player_action = PlayerAction(next_player(old_player_actions), PlayerAction.PREPARE_SHIFT)
                self.set_next(new_next_player_action)
            else:
                self._next = self._turn_states.index(old_next_player_action)

    def start(self):
        """ Starts the progression, informs player if necessary """
        if self._turn_states:
            self.set_next(index=0)

    def is_action_possible(self, player, action):
        """ Checks if the action can be performed by the player

        :param player: an instance of Player
        :param action: one of PlayerAction.MOVE_ACTION and PlayerAction.SHIFT_ACTION
        :return: true, iff the action is to be performed by the player
        """
        return (action is PlayerAction.MOVE_ACTION or action is PlayerAction.SHIFT_ACTION) and \
            self.next_player_action() == PlayerAction(player, action)

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
        self.set_next()

    def _next_action_is_prepare(self):
        return self.next_player_action() and self.next_player_action().is_prepare()

    def set_next(self, player_action=None, index=None):
        assert self._turn_states
        if player_action:
            next_index = self._turn_states.index(player_action)
        elif index is not None:
            next_index = index
        else:
            next_index = (self._next + 1) % len(self._turn_states)
        self._next = next_index
        if self.next_player_action().is_prepare():
            if self._prepare_delay:
                self._notify_turn_changed_listeners()
                Thread(target=self._delay_next_state, args=[self.next_player_action()]).start()
            else:
                self.set_next()
        else:
            self._notify_turn_changed_listeners()

    def restart_player_action(self):
        player_prepare_action = self.next_player_action().copy_with_prepare()
        self.set_next(player_action=player_prepare_action)

    def _delay_next_state(self, next_player_action):
        time.sleep(self._prepare_delay.total_seconds())
        # check that state was not changed, e.g. due to removed player
        if next_player_action == self.next_player_action():
            self.set_next()

    def next_player_action(self):
        """ Returns the next PlayerAction in the turn progression """
        try:
            return self._turn_states[self._next]
        except IndexError:
            return None

    @property
    def prepare_delay(self):
        """ Getter of prepare_delay """
        return self._prepare_delay

    def register_turn_changed_listener(self, listener):
        """ Register a listener which is notified whenever the turn changes.

        The listener will be called without an argument """
        self._turn_changed_listeners.append(listener)

    def _notify_turn_changed_listeners(self):
        player_action = self.next_player_action()
        if player_action and player_action.turn_callback:
            player_action.turn_callback(player_action.action)
        for listener in self._turn_changed_listeners:
            listener()


class Game:
    """ This class represents one played game

    The game is started as soon as the first player is added.
    By default, it creates a turn progression with a delay of one second.
    To use no delay, or a delay of your choice, provide a Turns instance."""
    MAX_PLAYERS = 4

    def __init__(self, identifier, board=None, players=None, turns=None):
        self._id = identifier
        self._players = players or []
        self._board = board or Board()
        self._turns = turns or Turns(prepare_delay=timedelta(milliseconds=800))
        self._turns.register_turn_changed_listener(self._notify_turn_listeners)
        self.previous_shift_location = None
        self._turn_listeners = []

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

    def unused_player_id(self):
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
        self._players.sort(key=lambda player: player.piece.piece_index)
        if len(self.players) == 1:
            self._turns.start()
        if len(self.players) == 2:
            self._turns.restart_player_action()

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

    def restart(self, new_board=None):
        """ Replaces the current board with a new one and resets the game.
        For all players, new pieces are created on the board """
        new_board.pieces.clear()
        for player in self._players:
            player.score = 0
            player.reset_board(new_board)
        self.previous_shift_location = None
        self._board = new_board
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

    def register_turn_change_listener(self, listener):
        """ Register a listener which is notified whenever the turn changes.

        The listener will be called with the game, the player to perform the next action and
        the type of the expected action.
        :param listener: a method with the parameters game, player and next_action"""
        self._turn_listeners.append(listener)

    def _notify_turn_listeners(self):
        next_player_action = self._turns.next_player_action()
        if next_player_action:
            for listener in self._turn_listeners:
                listener(game=self, next_player_action=next_player_action)

    def next_player(self):
        """ The player who is expected to perform the next action """
        return self._turns.next_player_action().player
