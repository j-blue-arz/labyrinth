""" Database access methods """
import json
import sqlite3
from flask import current_app, g
from .mapper.persistence import dto_to_game, game_to_dto


class DatabaseGateway:
    """ This gateway manages a database connection and
    encapsulates database access methods

    The class is implemented as a singleton, clients should get an instance
    via get_instance()."""

    def __init__(self):
        self._db_connection = None
        self._game_created_listeners = []

    @classmethod
    def get_instance(cls):
        """ Returns an instance of the gateway.

        The instance is stored in the global context """
        if "db_gateway" not in g:
            g.db_gateway = cls()
        return g.db_gateway

    def register_game_created_listener(self, listener):
        """ Registers a callback, which is called everytime a game is created from the database.
        The listener is called with the created game. """
        self._game_created_listeners.append(listener)

    def _notify_listeners(self, game):
        for listener in self._game_created_listeners:
            listener(game)

    def create_game(self, game, game_id=0):
        """ Inserts a game into the database """
        game_json = json.dumps(game_to_dto(game))
        self._db().execute(
            "INSERT INTO games(id, game_state) VALUES (?, ?)", (game_id, game_json)
        )
        self._notify_listeners(game)

    def load_game(self, game_id, for_update=False):
        """ Loads a game from the database """
        game_row = (
            self._db(exclusive=for_update)
            .execute("SELECT game_state FROM games WHERE id=?", (game_id,))
            .fetchone()
        )
        if game_row is None:
            return None
        return self._game_row_to_game(game_row)

    def load_all_games_before_action_timestamp(self, timestamp):
        """ Loads games where the player_action_timestamp is older than the given requested timestamp """
        game_rows = (
            self._db(exclusive=True)
            .execute("SELECT game_state FROM games WHERE player_action_timestamp<?", (timestamp,))
            .fetchall()
        )
        return [self._game_row_to_game(game_row) for game_row in game_rows]

    def _game_row_to_game(self, game_row):
        game = dto_to_game(json.loads(game_row["game_state"]))
        self._notify_listeners(game)
        return game

    def update_game(self, game_id, game):
        """ Updates a game in the database """
        game_json = json.dumps(game_to_dto(game))
        self._db().execute(
            "UPDATE games SET game_state=? WHERE ID=?", (game_json, game_id)
        )

    def update_action_timestamp(self, game_id, timestamp):
        """ Updates the player action timestamp for a game

        :param timestamp: expected to be an instance of datetime.timestamp"""
        self._db().execute(
            "UPDATE games SET player_action_timestamp=? WHERE ID=?",
            (timestamp, game_id),
        )

    def commit(self):
        """ Commits the transaction.

        If this method is not called (e.g. due to a prior exception), changes are lost. """
        self._db().commit()

    def _db(self, exclusive=False):
        """ Returns the database. The first time this method is called during a request,
        a sqlite connection is opened and stored in the global context """
        if not self._db_connection:
            self._db_connection = sqlite3.connect(
                current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
            )
            self._db_connection.row_factory = sqlite3.Row
            if exclusive:
                self._db_connection.isolation_level = None
                self._db_connection.execute("BEGIN EXCLUSIVE")
        return self._db_connection

    @classmethod
    def init_database(cls):
        """ Executes the schema definition """
        cls.get_instance()._db().executescript(
            """
        DROP TABLE IF EXISTS games;

        CREATE TABLE games (
            id INTEGER PRIMARY KEY,
            game_state TEXT NOT NULL,
            player_action_timestamp timestamp
        );
        """
        )

    @classmethod
    def close_database(cls):
        """ Closes the database connection """
        gateway = cls.get_instance()
        if gateway._db_connection:
            gateway._db_connection.close()
            gateway._db_connection = None
