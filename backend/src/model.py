""" The model of the game.

Game is the container for the entire state.
It consists of a Board, a leftover MazeCard, and a list of Players

Board manages the current state of the board, it manages a 2-d array of MazeCards.

MazeCard represents a single maze card, with outward connections and a rotation.

A Player represents a player, with a unique ID
and a reference to a maze card the piece is currently positioned on.
BoardLocation is a wrapper for a row and a column.
"""
from random import choice, randint


class BoardLocation:
    """A board location, defined by the row and the column.
    The location does now know the extent of the board"""

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



class Player:
    """ Represents a player
    Each player has a unique ID and,
    if positioned on the board, a reference to a MazeCard instance
    """

    def __init__(self, identifier=0, maze_card=None):
        self._id = identifier
        self.maze_card = maze_card

    @property
    def identifier(self):
        """ Getter for read-only identifier """
        return self._id


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
            raise ValueError("rotation must be divisible by 90")
        self._rotation = value % 360

    @property
    def doors(self):
        """ Getter of read-only doors """
        return self._doors

    @classmethod
    def reset_ids(cls):
        """ Resets the instance counter, such that a newly generated instance will have ID of 0 """
        cls.next_id = 0

    @classmethod
    def generate_random(cls):
        """ Generates a new instance randomly, with autoincreaseing ID """
        doors = choice([cls.STRAIGHT, cls.CORNER, cls.T_JUNCT])
        rotation = choice([0, 90, 180, 270])
        maze_card = MazeCard(cls.next_id, doors, rotation)
        cls.next_id = cls.next_id + 1
        return maze_card


class Board:
    """ Represent the state of the board.
    The state is maintained in a 2-d array of MazeCard instances.
    """

    BOARD_SIZE = 7
    def __init__(self):
        self._maze_cards = [[None for _ in range(self.BOARD_SIZE)] for _ in range(self.BOARD_SIZE)]
        self._insert_locations = set()
        for position in range(1, Board.BOARD_SIZE, 2):
            self._insert_locations.add(BoardLocation(0, position))
            self._insert_locations.add(BoardLocation(position, 0))
            self._insert_locations.add(BoardLocation(Board.BOARD_SIZE - 1, position))
            self._insert_locations.add(BoardLocation(position, Board.BOARD_SIZE - 1))

    def generate_random(self):
        """ Generates a random board state """
        self._maze_cards = [
            [MazeCard.generate_random() for _ in range(self.BOARD_SIZE)]
            for _ in range(self.BOARD_SIZE)]

    def random_maze_card(self):
        """ Returns a random MazeCard of the current board """
        return self._maze_cards[randint(0, self.BOARD_SIZE-1)][randint(0, self.BOARD_SIZE-1)]

    def __getitem__(self, location):
        """ Retrieves the maze card at a given location

        :param location: a BoardLocation instance
        :raises ValueError: if location is outside of the board
        :return: the MazeCard instance
        """
        if not self.is_inside(location):
            raise ValueError("Location is outside of the board")
        return self._maze_cards[location.row][location.column]

    def __setitem__(self, location, maze_card):
        """ sets the maze card at a given location

        :param location: a BoardLocation instance
        :raises ValueError: if location is outside of the board
        :param maze_card: the maze card to set
        """
        self._maze_cards[location.row][location.column] = maze_card

    def shift(self, insert_location, inserted_maze_card):
        """ Performs a shifting action on the board

        :param insert_location: the location of the inserted maze card
        :param inserted_maze_card: the maze card to insert
        :raises ValueError: for invalid insert location
        :return: the pushed out maze card
        """
        if insert_location not in self._insert_locations:
            raise ValueError("Invalid insert location")
        direction = self._determine_shift_direction(insert_location)
        shift_line_locations = []
        current_location = insert_location
        while current_location is not None:
            shift_line_locations.append(current_location)
            current_location = Board.neighbor(current_location, direction)
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
        :return: the direction as a tuple
        """
        if shift_location.row == cls.BOARD_SIZE - 1:
            return (-1, 0)
        if shift_location.row == 0:
            return (1, 0)
        if shift_location.column == cls.BOARD_SIZE - 1:
            return (0, -1)
        if shift_location.column == 0:
            return (0, 1)
        raise ValueError("Invalid insert location")

    @classmethod
    def neighbor(cls, location, direction):
        """ Determines the neighbor of a location, if possible.

        :param location: the location the neighbor is requested for
        :param direction: a tuple describing the position of the requested neighbor,
        relative to the given location, e.g. (-1, 0) for the northern neighbor
        :return: a new location in the given direction,
        or None, if the location is outside of the board's extent
        """
        new_location = location.add(*direction)
        if not cls.is_inside(new_location):
            new_location = None
        return new_location

    @classmethod
    def is_inside(cls, location):
        """ Determines if the given location is inside the board """
        return location.row >= 0 and \
            location.column >= 0 and \
            location.row < cls.BOARD_SIZE and \
            location.column < cls.BOARD_SIZE


class Game:
    """
    The state of a game of labyrinth.
    """
    MAX_PLAYERS = 4
    def __init__(self):
        self._players = []
        self._board = Board()
        self._leftover_card = MazeCard()

    @property
    def leftover_card(self):
        """ Getter for leftover card """
        return self._leftover_card

    @leftover_card.setter
    def leftover_card(self, value):
        """ Setter for leftover card """
        self._leftover_card = value

    @property
    def board(self):
        """ Getter for board """
        return self._board

    @property
    def players(self):
        """ Getter for players """
        return self._players

    @players.setter
    def players(self, players):
        """ Setter for players """
        self._players = players

    def accepts_players(self):
        """ Determines if there are empty seats for players to join """
        return len(self._players) < Game.MAX_PLAYERS

    def add_player(self):
        """ Adds a player and returns his id. Throws if game is full

        :raises ValueError: when game is full
        :return: id of the added player
        """
        if self.accepts_players():
            player_id = len(self._players)
            player = Player(player_id)
            self._players.append(player)
            return player_id
        raise ValueError("Game is full")

    def init_game(self):
        """ Randomly initializes the game state, with the currently connected players """
        self._board.generate_random()
        self._leftover_card = MazeCard.generate_random()
        for player in self._players:
            player.maze_card = self._board.random_maze_card()

    def shift(self, player_id, new_leftover_location, leftover_rotation):
        """ Performs a shifting action

        :param player_id: the shifting player's id
        :param new_leftover_location: the new location of the leftover MazeCard
        :param leftover_rotation: the rotation of the leftover MazeCard, in degrees
        (one of 0, 90, 180, 270)
        :raises ValueError: for invalid insert location, rotation value, or player id
        """
        self.find_player(player_id)
        self._leftover_card.rotation = leftover_rotation
        self._leftover_card = self._board.shift(new_leftover_location, self._leftover_card)

    def move(self, player_id, target_location):
        """ Performs a move action

        :param player_id: the moving player's id
        :param target_location: the board location to move to
        :raises ValueError: for invalid target location or player id
        """
        player = self.find_player(player_id)
        target = self._board[target_location]
        player.maze_card = target

    def find_player(self, player_id):
        """ Finds player by id """
        match = [player for player in self._players if player.identifier is player_id]
        if len(match) > 1:
            raise ValueError("Invalid state")
        elif not match:
            raise ValueError("No matching player in this game")
        return match[0]
