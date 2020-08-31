""" Controller

handles database access, calls functions on entities or use cases, performs exception mapping
Should not contain business logic"""
from flask import url_for

import labyrinth.model.factories as factory
import labyrinth.mapper.api as mapper
from labyrinth import exceptions
from labyrinth.database import DatabaseGateway
from labyrinth.model.exceptions import LabyrinthDomainException
from labyrinth.model import interactors
from labyrinth.model.game import Player
from labyrinth.model import computer


def add_player(game_id, player_request_dto):
    """ Adds a player to a game.
    Creates the game if it does not exist.
    After adding the player, the game is started.

    :param game_id: specifies the game
    :param player_request_dto: if this parameter is given, it contains information about the type of player to add
    :return: the added player
    """
    _ = interactors.OverduePlayerInteractor(game_repository())
    game = _get_or_create_game(game_id)
    is_computer, computation_method = mapper.dto_to_type(player_request_dto)
    player_id = _try(game.unused_player_id)
    player = None
    if not is_computer:
        player = Player(player_id)
    else:
        player = _try(lambda: computer.create_computer_player(compute_method=computation_method,
                                                              url_supplier=URLSupplier(), player_id=player_id))
    _try(lambda: game.add_player(player))
    if len(game.players) == 1:
        _try(game.start_game)
    DatabaseGateway.get_instance().update_game(game_id, game)
    DatabaseGateway.get_instance().commit()
    return mapper.player_to_dto(player)


def delete_player(game_id, player_id):
    """ Removes a player from a game

    :param game_id: specifies the game
    :param player_id: specifies the player to remove
    """
    _ = interactors.OverduePlayerInteractor(game_repository())
    game = _load_game_or_throw(game_id, for_update=True)
    _try(lambda: game.remove_player(player_id))
    DatabaseGateway.get_instance().update_game(game_id, game)
    DatabaseGateway.get_instance().commit()
    return ""


def change_game(game_id, game_request_dto):
    """ Changes game setup.

    Currently, the only option is to change the maze size.
    This will restart the game.
    :param game_id: specifies the game. Has to exist.
    :param game_request_dto: contains the new maze size."""
    new_size = mapper.dto_to_maze_size(game_request_dto)
    _ = interactors.OverduePlayerInteractor(game_repository())
    game = _load_game_or_throw(game_id)
    new_board = _try(lambda: factory.create_board(maze_size=new_size))
    _try(lambda: game.replace_board(new_board))
    DatabaseGateway.get_instance().update_game(game_id, game)
    DatabaseGateway.get_instance().commit()


def get_game_state(game_id):
    """ Returns the game state """
    _ = interactors.OverduePlayerInteractor(game_repository())
    game = _load_game_or_throw(game_id)
    return mapper.game_state_to_dto(game)


def perform_shift(game_id, player_id, shift_dto):
    """Performs a shift operation on the game."""
    location, rotation = mapper.dto_to_shift_action(shift_dto)
    _ = interactors.OverduePlayerInteractor(game_repository())
    interactor = interactors.PlayerActionInteractor(game_repository())
    _try(lambda: interactor.perform_shift(game_id, player_id, location, rotation))
    DatabaseGateway.get_instance().commit()


def perform_move(game_id, player_id, move_dto):
    """Performs a move operation on the game."""
    location = mapper.dto_to_move_action(move_dto)
    _ = interactors.OverduePlayerInteractor(game_repository())
    interactor = interactors.PlayerActionInteractor(game_repository())
    _try(lambda: interactor.perform_move(game_id, player_id, location))
    DatabaseGateway.get_instance().commit()


def get_computation_methods():
    """ Retrieves the available computation methods.
    These are either methods implemented in the backend, i.e. those in labyrinth.model.computer,
    or methods made available by dynamically loaded libraries """
    return computer.get_available_computation_methods()


def remove_overdue_players(overdue_timedelta):
    """ Uses OverduePlayerInteractor to remove players which block the game by not performing actions """
    interactor = interactors.OverduePlayerInteractor(game_repository())
    _try(lambda: interactor.remove_overdue_players(overdue_timedelta))
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
        return url_for("api.post_shift", game_id=game_id,
                       p_id=player_id, _external=True)

    def get_move_url(self, game_id, player_id):
        """ Generates a URL for the move operation """
        return url_for("api.post_move", game_id=game_id,
                       p_id=player_id, _external=True)
