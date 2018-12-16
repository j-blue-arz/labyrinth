""" Service Layer """
import server.domain.factories as factory
from . import exceptions
from . import database
from .mapper.api import player_state_to_dto, dto_to_shift_action, dto_to_move_action, dto_to_algorithm
from .domain.exceptions import LabyrinthDomainException
from .domain.model import Player
from .domain.computer import ComputerPlayer



def add_player(game_id, add_player_dto):
    """ Adds a player to a game.
    Creates the game if it does not exist.
    After adding the player, the game is started.

    :param game_id: specifies the game
    :param add_player_dto: if this parameter is given, it contains information about the type of computer player to add
    :raises exceptions.GAME_FULL: if the game is full
    :return: the id of the added player
    """
    game = _get_or_create_game(game_id)
    algorithm = dto_to_algorithm(add_player_dto)
    player_id = None
    if algorithm is None:
        player_id = _try(lambda: game.add_player(Player, {}))
    else:
        player_id = _try(lambda: game.add_player(ComputerPlayer, {"algorithm_name": algorithm}))
    _try(game.start_game)
    database.update_game(game_id, game)
    return player_id


def get_game_state(game_id, player_id):
    """ Returns the game state, as seen for the querying player """
    game = _load_game_or_throw(game_id)
    _try(lambda: game.get_player(player_id))
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
    game = factory.create_game()
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
        return model_operation()
    except LabyrinthDomainException as domain_exception:
        raise exceptions.domain_to_api_exception(domain_exception)
