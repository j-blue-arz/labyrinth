""" Controller

handles database access, calls functions on entities or use cases, performs exception mapping
Should not contain business logic"""
from datetime import timedelta

from flask import url_for, current_app

import labyrinth.model.factories as factory
import labyrinth.mapper.api as mapper
from labyrinth import exceptions
from labyrinth.database import DatabaseGateway
from labyrinth.model.exceptions import LabyrinthDomainException
from labyrinth.model import interactors
from labyrinth.model.game import Player
from labyrinth.model import bots

import labyrinth.event_logging as logging


def add_player(game_id, player_request_dto):
    """ Adds a player to a game.
    Creates the game if it does not exist.
    After adding the player, the game is started.

    :param game_id: specifies the game
    :param player_request_dto: if this parameter is given, it contains information about the type of player to add
    :return: the added player
    """
    _ = interactors.OverduePlayerInteractor(game_repository(), logging.get_logger())
    _ = interactors.UpdateOnTurnChangeInteractor(game_repository())
    game = _get_or_create_game(game_id)
    is_bot, computation_method = mapper.dto_to_type(player_request_dto)
    player_name = mapper.dto_to_player_name(player_request_dto)
    player_id = _try(game.unused_player_id)
    player = None
    if not is_bot:
        player = Player(player_id, player_name=player_name)
    else:
        player = _try(lambda: bots.create_bot(compute_method=computation_method,
                                              url_supplier=URLSupplier(), player_id=player_id,
                                              player_name=player_name))
    _try(lambda: game.add_player(player))
    DatabaseGateway.get_instance().update_game(game_id, game)
    DatabaseGateway.get_instance().commit()
    logging.get_logger().add_player(player_id, game_id=game_id, is_bot=is_bot, num_players=len(game.players))
    return mapper.player_to_dto(player)


def delete_player(game_id, player_id):
    """ Removes a player from a game

    :param game_id: specifies the game
    :param player_id: specifies the player to remove
    """
    _ = interactors.OverduePlayerInteractor(game_repository(), logging.get_logger())
    _ = interactors.UpdateOnTurnChangeInteractor(game_repository())
    game = _load_game_or_throw(game_id, for_update=True)
    _try(lambda: game.remove_player(player_id))
    DatabaseGateway.get_instance().update_game(game_id, game)
    DatabaseGateway.get_instance().commit()
    logging.get_logger().remove_player(player_id, game_id=game_id, num_players=len(game.players))
    return ""


def change_player_name(game_id, player_id, player_name_dto):
    """ Renames a player

    :param game_id: specifies the game
    :param player_id: specifies the player to remove
    :param player_name_dto: contains the new player name."""
    new_name = mapper.dto_to_player_name(player_name_dto)
    interactors.PlayerInteractor(game_repository()).change_name(game_id, player_id, new_name)
    DatabaseGateway.get_instance().commit()


def change_game(game_id, game_request_dto):
    """ Changes game setup.

    Currently, the only option is to change the maze size.
    This will restart the game.
    :param game_id: specifies the game. Has to exist.
    :param game_request_dto: contains the new maze size."""
    new_size = mapper.dto_to_maze_size(game_request_dto)
    _ = interactors.OverduePlayerInteractor(game_repository(), logging.get_logger())
    _ = interactors.UpdateOnTurnChangeInteractor(game_repository())
    game = _load_game_or_throw(game_id)
    new_board = _try(lambda: factory.create_board(maze_size=new_size))
    _try(lambda: game.restart(new_board))
    DatabaseGateway.get_instance().update_game(game_id, game)
    DatabaseGateway.get_instance().commit()


def get_game_state(game_id):
    """ Returns the game state """
    _ = interactors.OverduePlayerInteractor(game_repository(), logging.get_logger())
    _ = interactors.UpdateOnTurnChangeInteractor(game_repository())
    action_timeout = timedelta(seconds=int(current_app.config["OVERDUE_PLAYER_TIMEDELTA_S"]))
    interactor = interactors.ObserveGameInteractor(game_repository(), action_timeout=action_timeout)
    game, remaining_timedelta = _try(lambda: interactor.retrieve_game(game_id))
    game_state = mapper.game_state_to_dto(game, remaining_timedelta)
    DatabaseGateway.get_instance().commit()
    return game_state


def perform_shift(game_id, player_id, shift_dto):
    """Performs a shift operation on the game."""
    location, rotation = mapper.dto_to_shift_action(shift_dto)
    _ = interactors.OverduePlayerInteractor(game_repository(), logging.get_logger())
    _ = interactors.UpdateOnTurnChangeInteractor(game_repository())
    interactor = interactors.PlayerActionInteractor(game_repository())
    _try(lambda: interactor.perform_shift(game_id, player_id, location, rotation))
    DatabaseGateway.get_instance().commit()


def perform_move(game_id, player_id, move_dto):
    """Performs a move operation on the game."""
    location = mapper.dto_to_move_action(move_dto)
    _ = interactors.OverduePlayerInteractor(game_repository(), logging.get_logger())
    _ = interactors.UpdateOnTurnChangeInteractor(game_repository())
    interactor = interactors.PlayerActionInteractor(game_repository())
    _try(lambda: interactor.perform_move(game_id, player_id, location))
    DatabaseGateway.get_instance().commit()


def get_computation_methods():
    """ Retrieves the available computation methods.

    These can be used to add bots. """
    return bots.get_available_computation_methods()


def remove_overdue_players(overdue_timedelta):
    """ Uses OverduePlayerInteractor to remove players which block the game by not performing actions """
    interactor = interactors.OverduePlayerInteractor(game_repository(), logging.get_logger())
    _try(lambda: interactor.remove_overdue_players(overdue_timedelta))
    DatabaseGateway.get_instance().commit()


def remove_unobserved_games(unobserved_period):
    """ Uses UnobservedGamesInteractor to remove games which have not been observed for the given period """
    interactor = interactors.UnobservedGamesInteractor(game_repository(), logging.get_logger())
    removed_ids = _try(lambda: interactor.remove_unobserved_games(unobserved_period))
    for game_id in removed_ids:
        logging.get_logger().remove_game(game_id)
    DatabaseGateway.get_instance().commit()


def game_repository():
    return interactors.GameRepository(DatabaseGateway.get_instance())


def _get_or_create_game(game_id):
    game = DatabaseGateway.get_instance().load_game(game_id)
    if game is None:
        game = _create_game(game_id)
    return game


def _create_game(game_id):
    game = factory.create_game(game_id=game_id)
    DatabaseGateway.get_instance().create_game(game, game_id)
    logging.get_logger().add_game(game_id)
    return game


def _load_game_or_throw(game_id, for_update=False):
    game = DatabaseGateway.get_instance().load_game(game_id, for_update=for_update)
    if game is None:
        raise exceptions.GAME_NOT_FOUND_API_EXCEPTION
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
        return self._get_url(game_id, player_id, "api.post_shift")

    def get_move_url(self, game_id, player_id):
        """ Generates a URL for the move operation """
        return self._get_url(game_id, player_id, "api.post_move")

    def _get_url(self, game_id, player_id, api_method):
        internal_url = current_app.config["INTERNAL_URL"] if "INTERNAL_URL" in current_app.config else None
        if internal_url:
            return internal_url + url_for(api_method, game_id=game_id,
                                          p_id=player_id, _external=False)
        else:
            return url_for(api_method, game_id=game_id,
                           p_id=player_id, _external=True)
