""" Database access methods """
import json
import sqlite3
from flask import current_app, g
from .mapper.persistence import dto_to_game, game_to_dto


def create_game(game, game_id=0):
    """ Inserts a game into the database """
    game_json = json.dumps(game_to_dto(game))
    _get_database().execute(
        "INSERT INTO games(id, game_state) VALUES (?, ?)", (game_id, game_json)
    )
    _get_database().commit()


def load_game(game_id):
    """ Loads a game from the database """
    game_row = _get_database().execute(
        "SELECT game_state FROM games WHERE id=?", (game_id,)
    ).fetchone()
    if game_row is None:
        return None
    return dto_to_game(json.loads(game_row["game_state"]))


def update_game(game_id, game):
    """ Updates a game in the database """
    game_json = json.dumps(game_to_dto(game))
    _get_database().execute(
        "UPDATE games SET game_state=? WHERE ID=?", (game_json, game_id)
    )
    _get_database().commit()


def _get_database():
    """ Returns the database. The first time this method is called during a request,
    a sqlite connection is opened and stores it in the global context """
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db


def init_database():
    """ Executes the schema definition """
    database = _get_database()
    database.executescript("""
        DROP TABLE IF EXISTS games;

        CREATE TABLE games (
            id INTEGER PRIMARY KEY,
            game_state TEXT NOT NULL
        );
    """)


def close_database(exception=None):
    """ Closes the database connection """
    database = g.pop('db', None)

    if database is not None:
        database.close()
