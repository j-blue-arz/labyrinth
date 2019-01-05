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
from random import choice
from . import exceptions
from .maze_algorithm import Graph


class BoardLocation:
    """A board location, defined by the row and the column.
    The location does now know the extent of the maze.
    """

    def __init__(self, row, column):
        self.row = row
        self.column = column

    def add(self, row_delta, column_delta):
        """ Returns a new BoardLocation by adding the deltas to the current location """
        return BoardLocation(self.row + row_delta, self.column + column_delta)

    def __eq__(self, other):
        return isinstance(self, type(other)) and \
            self.column == other.column and \
            self.row == other.row

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.row, self.column))

    def __str__(self):
        return "({}, {})".format(self.row, self.column)

    def __repr__(self):
        return self.__str__()


class MazeCard:
    """ Represents one maze card
    The doors field defines the type of the card.
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
    next_id = 0
    _DIRECTION_TO_DOOR = {(-1, 0): "N", (0, 1): "E", (1, 0): "S", (0, -1): "W"}

    def __init__(self, identifier=0, doors=STRAIGHT, rotation=0):
        self._doors = doors
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
    def doors(self):
        """ Getter of read-only doors """
        return self._doors

    def has_out_path(self, direction):
        """ Returns whether there is an outgoing path
        in a given direction, taking the rotation into account.

        :param direction: a tuple describing the direction of the path, e.g. (-1, 0) for north
        :return: true iff there is a path in the given direction
        """
        door = self._DIRECTION_TO_DOOR[direction]
        door_index = "NESW".find(door)
        turns = (self._rotation // 90)
        adapted_index = (door_index - turns + 4) % 4
        adapted_door = "NESW"[adapted_index]
        return adapted_door in self._doors

    def out_paths(self):
        """ Returns an iterator over all directions
        with outgoing paths, taking rotation into account.
        """
        for direction in self._DIRECTION_TO_DOOR:
            if self.has_out_path(direction):
                yield direction

    @classmethod
    def reset_ids(cls):
        """ Resets the instance counter, such that a newly generated instance will have ID of 0 """
        cls.next_id = 0

    @classmethod
    def create_instance(cls, doors, rotation):
        """Generates a new instance, with autoincreasing ID.
        """
        maze_card = MazeCard(cls.next_id, doors, rotation)
        cls.next_id = cls.next_id + 1
        return maze_card

    def __eq__(self, other):
        return isinstance(self, type(other)) and \
            self.identifier == other.identifier

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.identifier))

    def __str__(self):
        return "(MazeCard: identifier: {}, rotation: {}, doors: {})".format(self.identifier, self.rotation, self.doors)

    def __repr__(self):
        return self.__str__()


class Piece:
    """ Represents a player's piece
    Each piece has a reference to a MazeCard instance as its position.
    """

    def __init__(self, maze_card: MazeCard):
        self.maze_card = maze_card


class Maze:
    """ Represent the state of the maze.
    The state is maintained in a 2-d array of MazeCard instances.
    """
    MAZE_SIZE = 7

    def __init__(self):
        self._maze_cards = [[None for _ in range(self.MAZE_SIZE)] for _ in range(self.MAZE_SIZE)]

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
        for location in self.maze_locations():
            if self[location] == maze_card:
                return location
        return None

    def shift(self, insert_location, inserted_maze_card):
        """ Performs a shifting action on the maze

        :param insert_location: the location of the inserted maze card
        :param inserted_maze_card: the maze card to insert
        :raises InvalidShiftLocationException: for invalid insert location
        :return: the pushed out maze card
        """
        self._validate_insert_location(insert_location)
        direction = self._determine_shift_direction(insert_location)
        shift_line_locations = []
        current_location = insert_location
        while current_location is not None:
            shift_line_locations.append(current_location)
            current_location = Maze._neighbor(current_location, direction)
        pushed_out = self[shift_line_locations[-1]]
        self._shift_all(shift_line_locations)
        self[shift_line_locations[0]] = inserted_maze_card
        return pushed_out

    def _shift_all(self, shift_locations):
        """ Shifts the maze cards along the given locations """
        for source, target in reversed(list(zip(shift_locations, shift_locations[1:]))):
            self[target] = self[source]

    @classmethod
    def _determine_shift_direction(cls, shift_location):
        """ Returns the direction to shift to for a given location

        :param shift_location: the location of the pushed in maze card
        :raises InvalidShiftLocationException: if the location is not on the border
        :return: the direction as a tuple
        """
        if shift_location.row == cls.MAZE_SIZE - 1:
            return (-1, 0)
        if shift_location.row == 0:
            return (1, 0)
        if shift_location.column == cls.MAZE_SIZE - 1:
            return (0, -1)
        if shift_location.column == 0:
            return (0, 1)
        raise exceptions.InvalidShiftLocationException(
            "Location {} is not shiftable (not on border)".format(str(shift_location)))

    @classmethod
    def _neighbor(cls, location, direction):
        """ Determines the neighbor of a location, if possible.

        :param location: the location the neighbor is requested for
        :param direction: a tuple describing the position of the requested neighbor,
        relative to the given location, e.g. (-1, 0) for the northern neighbor
        :return: a new location in the given direction,
        or None, if the location is outside of the maze's extent
        """
        new_location = location.add(*direction)
        if not cls.is_inside(new_location):
            new_location = None
        return new_location

    @classmethod
    def is_inside(cls, location):
        """ Determines if the given location is inside the maze """
        return location.row >= 0 and \
            location.column >= 0 and \
            location.row < cls.MAZE_SIZE and \
            location.column < cls.MAZE_SIZE

    @classmethod
    def maze_locations(cls):
        """ Returns an iterator of all BoardLocations """
        for row in range(cls.MAZE_SIZE):
            for column in range(cls.MAZE_SIZE):
                yield BoardLocation(row, column)

    @classmethod
    def _validate_location(cls, location):
        if not cls.is_inside(location):
            raise exceptions.InvalidLocationException("Location {} is outside of the maze.".format(str(location)))

    def _validate_insert_location(self, insert_location):
        self._validate_location(insert_location)


class Board:
    """
    The board state of a game of labyrinth.
    """

    def __init__(self, maze=None, leftover_card=None, objective_maze_card=None):
        self._pieces = []
        if not maze:
            maze = Maze()
        self._maze = maze
        if not leftover_card:
            leftover_card = MazeCard()
        self._leftover_card = leftover_card
        if not objective_maze_card:
            objective_maze_card = self._random_unoccupied_maze_card()
        self._objective_maze_card = objective_maze_card
        self._start_locations = [
            BoardLocation(0, 0),
            BoardLocation(0, self._maze.MAZE_SIZE - 1),
            BoardLocation(self._maze.MAZE_SIZE - 1, self._maze.MAZE_SIZE - 1),
            BoardLocation(self._maze.MAZE_SIZE - 1, 0)]
        self.validate_moves = True
        self.insert_locations = set()
        for position in range(1, Maze.MAZE_SIZE, 2):
            self.insert_locations.add(BoardLocation(0, position))
            self.insert_locations.add(BoardLocation(position, 0))
            self.insert_locations.add(BoardLocation(Maze.MAZE_SIZE - 1, position))
            self.insert_locations.add(BoardLocation(position, Maze.MAZE_SIZE - 1))

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

    def clear_pieces(self):
        """ Removes all pieces currently on the board """
        self._pieces.clear()

    def create_piece(self):
        """ Creates and places a piece on the board.
        Generates new objective, because the old one could be the same as the new piece's starting location. """

        def next_least_pieces_start_location():
            least_pieces = 1000
            least_pieces_location = None
            for location in self._start_locations:
                num_pieces = len([piece for piece in self.pieces if piece.maze_card is self.maze[location]])
                if num_pieces < least_pieces:
                    least_pieces_location = location
                    least_pieces = num_pieces
            return least_pieces_location

        next_location = next_least_pieces_start_location()
        piece = Piece(self._maze[next_location])
        self._pieces.append(piece)
        self._objective_maze_card = self._random_unoccupied_maze_card()
        return piece

    def remove_piece(self, piece):
        """ Removes a piece from the board """
        self._pieces.remove(piece)

    def shift(self, new_leftover_location, leftover_rotation):
        """ Performs a shifting action """
        self._validate_insert_location(new_leftover_location)
        self._leftover_card.rotation = leftover_rotation
        pushed_card = self._leftover_card
        self._leftover_card = self._maze.shift(new_leftover_location, self._leftover_card)
        for card_piece in self._find_pieces_by_maze_card(self._leftover_card):
            card_piece.maze_card = pushed_card

    def move(self, piece, target_location):
        """ Performs a move action. Returns True iff objective was reached. """
        piece_location = self._maze.maze_card_location(piece.maze_card)
        target = self._maze[target_location]
        self._validate_move_location(piece_location, target_location)
        piece.maze_card = target
        if target == self.objective_maze_card:
            self._objective_maze_card = self._random_unoccupied_maze_card()
            return True
        return False

    def opposing_insert_location(self, insert_location):
        """ Returns the insert location directly opposite of the given location """
        row, column = insert_location.row, insert_location.column
        limit = self.maze.MAZE_SIZE - 1
        borders = {0, limit}
        if row in borders:
            return BoardLocation(limit - row, column)
        if column in borders:
            return BoardLocation(row, limit - column)
        raise exceptions.InvalidStateException("Location {} is not on the border".format(insert_location))


    def _validate_move_location(self, piece_location, target_location):
        if self.validate_moves:
            if not Graph(self._maze).is_reachable(piece_location, target_location):
                raise exceptions.MoveUnreachableException("Locations {} and {} are not connected".format(
                    piece_location, target_location))

    def _validate_insert_location(self, insert_location):
        if insert_location not in self.insert_locations:
            raise exceptions.InvalidShiftLocationException(
                "Location {} is not shiftable (fixed maze cards)".format(str(insert_location)))

    def _find_pieces_by_maze_card(self, maze_card):
        """ Finds pieces whose maze_card field matches the given maze card

        :param maze_card: an instance of MazeCard
        """
        return [piece for piece in self._pieces if piece.maze_card is maze_card]

    def _random_unoccupied_maze_card(self):
        """ Finds a random unoccupied maze card,
        where a maze card is either occupied by a player's piece or by a
        player's objective
        """
        maze_cards = set([self._maze[location]
                          for location in self._maze.maze_locations()] + [self._leftover_card])
        for piece in self._pieces:
            maze_cards.discard(piece.maze_card)
        return choice(tuple(maze_cards))


class Player:
    """ This class represents a player playing a game """

    def __init__(self, identifier=None, game=None, piece=None, board=None):
        self._id = identifier
        self._board = board
        self._piece = piece
        self._game = game

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
        found = False
        for player_action in self._player_actions:
            if player_action.player is player:
                found = True
        if not found:
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

    def start(self, next_action=None):
        """ Starts the progression, informs player if necessary """
        if next_action:
            self._next = self._player_actions.index(next_action)
        else:
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
        if players:
            self._players = players
        else:
            self._players = []
        if board:
            self._board = board
        else:
            self._board = Board()
        if turns:
            self._turns = turns
        else:
            self._turns = Turns()
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

    def add_player(self, player_class, **player_class_kwargs):
        """Creates a player and adds it to the game. Throws if the game is full.

        :param player: a class, descendant of Player
        :param player_class_kwargs: a dictionary of keyword arguments for constructor of player_class
        :return: the ID of the player
        """
        if len(self._players) >= self.MAX_PLAYERS:
            raise exceptions.GameFullException("Already {} players playing the game.".format(self.MAX_PLAYERS))
        next_id = max([player.identifier for player in self._players], default=0) + 1
        player = player_class(identifier=next_id, game=self, **player_class_kwargs)
        player.set_board(self._board)
        player.register_in_turns(self._turns)
        self._players.append(player)
        return player.identifier

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

    def change_player(self, player_id, player_class, **player_class_kwargs):
        """ Changes the type of a player.

        Replaces player with given ID by a newly created player.
        :param player_id: the ID of the player to chane
        :param player_class: a class, descendant of Player
        :param player_class_kwargs: a dictionary of keyword arguments for constructor of player_class
        """
        old_player = self.get_player(player_id)
        new_player = player_class(identifier=player_id, game=self,
                                  piece=old_player.piece, board=old_player.board, **player_class_kwargs)
        self.players[self.players.index(old_player)] = new_player
        self.start_game()

    def start_game(self):
        """ starts the turn progression """
        self._turns.init(self.players)
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
            self._board.move(player.piece, target_location)
        self._turns.perform_action(player, PlayerAction.MOVE_ACTION)

    def get_enabled_shift_locations(self):
        """ Returns all currently enabled shift locations.
        These are the shift locations of the board, without the shift location of the previous turn
        """
        opposing_shift_location = None
        if self.previous_shift_location:
            opposing_shift_location = self.board.opposing_insert_location(self.previous_shift_location)
        return self.board.insert_locations.difference({opposing_shift_location})

    def _validate_pushback_rule(self, shift_location):
        """ Checks if the requested shift location is different to the shift location of the previous turn
        Throws exception if this rule is violated
        """
        opposing_shift_location = None
        if self.previous_shift_location:
            opposing_shift_location = self.board.opposing_insert_location(self.previous_shift_location)
        if shift_location == opposing_shift_location:
            raise exceptions.InvalidShiftLocationException(
                "Location {} is not shiftable (no-pushback rule)".format(str(shift_location)))
