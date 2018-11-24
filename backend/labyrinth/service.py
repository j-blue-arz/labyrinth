""" Service Layer """
import json
from labyrinth.db import get_database
from labyrinth.mapper import dto_to_game, game_to_dto, dto_to_shift_action, dto_to_move_action, exception_to_dto
from labyrinth.model import Game


class ApiException(Exception):
    """ Exception which is translated to a HTTP Response """

    KNOWN_EXCEPTIONS = {
        "GAME_FULL": ("Number of players has reached game limit.", 400),
        "INVALID_ACTION": ("The sent action is invalid.", 400),
        "GAME_NOT_FOUND": ("The game does not exist.", 404),
        "PLAYER_NOT_IN_GAME": ("The player does not take part in this game.", 400),
        "UNKNOWN_ERROR": ("An unknown error has occurred.", 400)
    }

    def __init__(self, key, message, status_code):
        super(ApiException, self).__init__(message)
        self.key = key
        self.message = message
        self.status_code = status_code

    def to_dto(self):
        """ Maps this object to a DTO to be transferred by the API """
        return exception_to_dto(self)

    @classmethod
    def from_key(cls, key):
        """ Creates a new ApiException from a known dictionary of possible keys """
        if not key in cls.KNOWN_EXCEPTIONS:
            return cls.from_key("UNKNOWN_ERROR")
        message, status_code = cls.KNOWN_EXCEPTIONS[key]
        return ApiException(key, message, status_code)


def add_player(game_id):
    game = load_game(game_id)
    if game is None:
        game = create_game(game_id)
    player_id = game.add_player()
    if player_id is not None:
        game.init_game()
        update_game(game_id, game)
        return player_id
    raise ApiException.from_key("GAME_FULL")


def load_game(game_id):
    game_row = get_database().execute(
        "SELECT game_state FROM games WHERE id=?", (game_id,)
    ).fetchone()
    if game_row is None:
        return None
    return dto_to_game(json.loads(game_row["game_state"]))


def create_game(game_id):
    game = Game()
    game.init_game()
    game_json = json.dumps(game_to_dto(game))
    get_database().execute(
        "INSERT INTO games(id, game_state) VALUES (0, 'asdf')"  # , (game_id, game_json)
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
    game = _load_game_or_throw(game_id)
    try:
        game.find_player(player_id)
    except:
        raise ApiException.from_key("PLAYER_NOT_IN_GAME")
    return game_to_dto(_load_game_or_throw(game_id), player_id=player_id)


def perform_shift(game_id, player_id, shift_dto):
    location, rotation = dto_to_shift_action(shift_dto)
    game = _load_game_or_throw(game_id)
    try:
        game.shift(player_id, location, rotation)
    except ValueError as exception:
        if "rotation" in str(exception):
            raise ApiException.from_key("INVALID_ACTION")
        if "location" in str(exception):
            raise ApiException.from_key("INVALID_ACTION")
        elif "player" in str(exception):
            raise ApiException.from_key("PLAYER_NOT_IN_GAME")
        raise ApiException.from_key("UNKNOWN_ERROR")
    update_game(game_id, game)


def perform_move(game_id, player_id, move_dto):
    location = dto_to_move_action(move_dto)
    game = _load_game_or_throw(game_id)
    try:
        game.move(player_id, location)
    except ValueError as exception:
        if "location" in str(exception):
            raise ApiException.from_key("INVALID_ACTION")
        elif "player" in str(exception):
            raise ApiException.from_key("PLAYER_NOT_IN_GAME")
        raise ApiException.from_key("UNKNOWN_ERROR")
    update_game(game_id, game)


def _load_game_or_throw(game_id):
    game = load_game(game_id)
    if game is None:
        raise ApiException.from_key("GAME_NOT_FOUND")
    return game
