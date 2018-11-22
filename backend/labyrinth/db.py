""" Database access methods """
import sqlite3

from flask import current_app, g


def get_database():
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
    database = get_database()
    with current_app.open_resource('schema.sql') as file:
        database.executescript(file.read().decode('utf8'))


def close_database(exception=None):
    """ Closes the database connection """
    database = g.pop('db', None)

    if database is not None:
        database.close()
    