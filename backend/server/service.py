""" Service Layer """
from . import exceptions
from . import database
from .mapper import player_state_to_dto, dto_to_shift_action, dto_to_move_action
from .domain.model import Game
from .domain.exceptions import LabyrinthDomainException



def add_player(game_id):
    """ Adds a player to a game.
    Creates the game if it does not exist.
    After adding the player, the game state is randomly generated.

    :param game_id: specifies the game
    :raises exceptions.GAME_FULL: if the game is full
    :return: the id of the added player
    """
    game = _get_or_create_game(game_id)
    player_id = game.add_player()
    if player_id is not None:
        game.init_game()
        database.update_game(game_id, game)
        return player_id
    raise exceptions.GAME_FULL()

def get_game_state(game_id, player_id):
    """ Returns the game state, as seen for the querying player """
    game = _load_game_or_throw(game_id)
    _try(lambda: game.check_player(player_id))
    return player_state_to_dto(game, player_id)


def perform_shift(game_id, player_id, shift_dto):
    """Performs a shift operation on the game."""
    location, rotation = dto_to_shift_action(shift_dto)
    game = _load_game_or_throw(game_id)
    _try(lambda: game.shift(player_id, location, rotation))
    database.update_game(game_id, game)


def perform_move(game_id, player_id, move_dto):
    """Performs a move operation on the game."""
    location = dto_to_move_action(move_dto)
    game = _load_game_or_throw(game_id)
    _try(lambda: game.move(player_id, location))
    database.update_game(game_id, game)

def _get_or_create_game(game_id):
    game = database.load_game(game_id)
    if game is None:
        game = _create_game(game_id)
    return game

def _create_game(game_id):
    game = Game()
    game.init_game()
    database.create_game(game, game_id)
    return game

def _load_game_or_throw(game_id):
    game = database.load_game(game_id)
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
