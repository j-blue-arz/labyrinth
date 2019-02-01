""" Service Layer """
from flask import url_for
import server.model.factories as factory
import server.mapper.api as mapper
from . import exceptions
from . import database
from .model.exceptions import LabyrinthDomainException
from .model.game import Player
from .model.computer import ComputerPlayer

def add_player(game_id, player_request_dto):
    """ Adds a player to a game.
    Creates the game if it does not exist.
    After adding the player, the game is started.

    :param game_id: specifies the game
    :param player_request_dto: if this parameter is given, it contains information about the type of player to add
    :return: the id of the added player
    """
    game = _get_or_create_game(game_id)
    player_type = mapper.dto_to_type(player_request_dto)
    if player_type is None:
        player_type = "human"
    player_id = None
    if player_type == "human":
        player_id = _try(lambda: game.add_player(Player))
    else:
        player_id = _try(lambda: game.add_player(
            ComputerPlayer, algorithm_name=player_type, url_supplier=URLSupplier()))
    _try(game.start_game)
    database.update_game(game_id, game)
    return player_id


def delete_player(game_id, player_id):
    """ Removes a player from a game

    :param game_id: specifies the game
    :param player_id: specifies the player to remove
    """
    game = _load_game_or_throw(game_id)
    _try(lambda: game.remove_player(player_id))
    database.update_game(game_id, game)
    return ""


def replace_player(game_id, player_id, player_request_dto):
    """ Changes a player in a game.

    :param game_id: specifies the game. Has to exist.
    :param player_id: specifies the player to remove
    :param player_request_dto: contains information about the type of player to add.
    Currently the only supported option is to replace a human player by a computer player.
    """
    player_type = mapper.dto_to_type(player_request_dto)
    if player_type == 'human':
        raise exceptions.INVALID_ARGUMENTS()
    else:
        game = _load_game_or_throw(game_id)
        game.change_player(player_id,
                           ComputerPlayer, algorithm_name=player_type, url_supplier=URLSupplier())
        database.update_game(game_id, game)


def get_game_state(game_id):
    """ Returns the game state """
    game = _load_game_or_throw(game_id)
    return mapper.player_state_to_dto(game)


def perform_shift(game_id, player_id, shift_dto):
    """Performs a shift operation on the game."""
    location, rotation = mapper.dto_to_shift_action(shift_dto)
    game = _load_game_or_throw(game_id)
    _try(lambda: game.shift(player_id, location, rotation))
    database.update_game(game_id, game)


def perform_move(game_id, player_id, move_dto):
    """Performs a move operation on the game."""
    location = mapper.dto_to_move_action(move_dto)
    game = _load_game_or_throw(game_id)
    _try(lambda: game.move(player_id, location))
    database.update_game(game_id, game)


def _get_or_create_game(game_id):
    game = database.load_game(game_id)
    if game is None:
        game = _create_game(game_id)
    return game


def _create_game(game_id):
    game = factory.create_game(original=True)
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


class URLSupplier:
    """ A class which supplies request URLs for the API """

    def get_shift_url(self, game_id, player_id):
        """ Generates a URL for the shift operation """
        return url_for("api.post_shift", game_id=game_id,
                       p_id=player_id, _external=True)

    def get_move_url(self, game_id, player_id):
        """ Generates a URL for the move operation """
        return url_for("api.post_move", game_id=game_id,
                       p_id=player_id, _external=True)
