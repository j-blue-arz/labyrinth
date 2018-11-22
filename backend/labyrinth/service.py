""" Service Layer """
import json
from labyrinth.db import get_database
from labyrinth.mapper import dto_to_game, game_to_dto, dto_to_shift_action, dto_to_move_action
from labyrinth.model import Game


def add_player(game_id):
    game = load_game(game_id)
    if game is None:
        game = create_game(game_id)
    player_id = game.add_player()
    game.init_game()
    update_game(game_id, game)
    return player_id


def load_game(game_id):
    game_row = get_database().execute(
        "SELECT game_state FROM games WHERE id=?", (game_id,)
    ).fetchone()
    try:
        return dto_to_game(json.loads(game_row["game_state"]))
    except (AttributeError, TypeError):
        return None


def create_game(game_id):
    game = Game()
    game.init_game()
    game_json = json.dumps(game_to_dto(game))
    get_database().execute(
        "INSERT INTO games(id, game_state) VALUES (0, 'asdf')"#, (game_id, game_json)
    )
    get_database().commit()
    return game


def update_game(game_id, game):
    game_json = json.dumps(game_to_dto(game))
    get_database().execute(
        "UPDATE games SET game_state=? WHERE ID=?", (game_json, game_id)
    )
    get_database().commit()


def get_game_state(game_id, player_id):
    return game_to_dto(load_game(game_id), player_id=player_id)


def perform_shift(game_id, player_id, shift_dto):
    location, rotation = dto_to_shift_action(shift_dto)
    game = load_game(game_id)
    game.shift(player_id, location, rotation)
    update_game(game_id, game)


def perform_move(game_id, player_id, move_dto):
    location = dto_to_move_action(move_dto)
    game = load_game(game_id)
    game.move(player_id, location)
    update_game(game_id, game)
