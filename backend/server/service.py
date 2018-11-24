""" Service Layer """
import json
from . import exceptions
from . import db
from .mapper import dto_to_game, game_to_dto, dto_to_shift_action, dto_to_move_action
from .domain.model import Game
from .domain.exceptions import LabyrinthDomainException



def add_player(game_id):
    game = load_game(game_id)
    if game is None:
        game = create_game(game_id)
    player_id = game.add_player()
    if player_id is not None:
        game.init_game()
        update_game(game_id, game)
        return player_id
    raise exceptions.GAME_FULL()


def load_game(game_id):
    game_row = db.get_database().execute(
        "SELECT game_state FROM games WHERE id=?", (game_id,)
    ).fetchone()
    if game_row is None:
        return None
    return dto_to_game(json.loads(game_row["game_state"]))


def create_game(game_id):
    game = Game()
    game.init_game()
    game_json = json.dumps(game_to_dto(game))
    db.get_database().execute(
        "INSERT INTO games(id, game_state) VALUES (?, ?)", (game_id, game_json)
    )
    db.get_database().commit()
    return game


def update_game(game_id, game):
    game_json = json.dumps(game_to_dto(game))
    db.get_database().execute(
        "UPDATE games SET game_state=? WHERE ID=?", (game_json, game_id)
    )
    db.get_database().commit()


def get_game_state(game_id, player_id):
    game = _load_game_or_throw(game_id)
    _try(lambda: game.find_player(player_id))
    return game_to_dto(_load_game_or_throw(game_id), player_id=player_id)


def perform_shift(game_id, player_id, shift_dto):
    location, rotation = dto_to_shift_action(shift_dto)
    game = _load_game_or_throw(game_id)
    _try(lambda: game.shift(player_id, location, rotation))
    update_game(game_id, game)


def perform_move(game_id, player_id, move_dto):
    location = dto_to_move_action(move_dto)
    game = _load_game_or_throw(game_id)
    _try(lambda: game.move(player_id, location))
    update_game(game_id, game)


def _load_game_or_throw(game_id):
    game = load_game(game_id)
    if game is None:
        raise exceptions.GAME_NOT_FOUND()
    return game

def _try(model_operation):
    """ performs the given operation on the model.
    On exception, it raises the corresponding ApiException

    :param model_operation: an operation to be performed, e.g.
    lambda: game.move(player_id, location)
    """
    try:
        model_operation()
    except LabyrinthDomainException as domain_exception:
        raise exceptions.domain_to_api_exception(domain_exception)
