""" Game-related use case interactors.

Also defines the GameRepository.
"""

from datetime import datetime, timedelta

from flask import has_request_context
from labyrinth.database import DatabaseGateway

from labyrinth.model import exceptions
import labyrinth.event_logging as logging


class PlayerActionInteractor:
    """ Interactor class which handles player actions (shift and move)

    Both methods (perform_shift and perform_move) follow the same line:
    load the game, perform the action, update the game state
    """
    def __init__(self, game_repository):
        self._game_repository = game_repository

    def perform_shift(self, game_id, player_id, shift_location, shift_rotation):
        game = self._game_repository.find_by_id(game_id)
        game.shift(player_id, shift_location, shift_rotation)
        self._game_repository.update(game)

    def perform_move(self, game_id, player_id, move_location):
        game = self._game_repository.find_by_id(game_id)
        game.move(player_id, move_location)
        self._game_repository.update(game)


class UpdateOnTurnChangeInteractor:
    """ Interactor class which persists asynchronous turn changes. """
    def __init__(self, game_repository):
        self._game_repository = game_repository
        self._game_repository.register_game_created_listener(self._on_game_creation)

    def _on_game_creation(self, game):
        game.register_turn_change_listener(self._update_player_action_async)

    def _update_player_action_async(self, game, next_player_action):
        if not has_request_context():
            with self._game_repository.managed_gateway() as gateway:
                gateway.update_turn_state(game.identifier, next_player_action)


class OverduePlayerInteractor:
    """ This interactor detects and removes players who are expected to perform an action,
    but have failed to do so for some period of time. """

    def __init__(self, game_repository, logger):
        self._game_repository = game_repository
        self._game_repository.register_game_created_listener(self._on_game_creation)
        self._logger = logger

    def remove_overdue_players(self, overdue_timedelta=timedelta(seconds=60)):
        """ Detects and removes players which are required to play next.

        Checks all currently running games.
        Players are automatically removed if it is their turn to play and
        they have not performed an action for a certain amount of time. """
        threshold = datetime.now() - overdue_timedelta
        games = self._game_repository.find_all_before_action_timestamp(threshold)
        for game in games:
            if game.players:
                player_id_to_remove = game.next_player().identifier
                game.remove_player(player_id_to_remove)
                self._game_repository.update(game)
                self._logger.remove_player(player_id_to_remove, game_id=game.identifier,
                                           num_players=len(game.players))

    def _on_game_creation(self, game):
        game.register_turn_change_listener(self._turn_change_listener)

    def _turn_change_listener(self, game, next_player_action):
        if next_player_action.is_prepare():
            self._game_repository.update_action_timestamp(game, datetime.now())


class ObserveGameInteractor:
    """ This interactor retrieves and returns the current game.

    It updates a timestamp on the game if the current one is too old.
    """
    def __init__(self, game_repository, update_period=timedelta(minutes=15)):
        self._game_repository = game_repository
        self._update_period = update_period

    def retrieve_game(self, game_id):
        game, last_observed_timestamp = self._game_repository.find_by_id(game_id, with_last_observed=True)
        if self._update_required(last_observed_timestamp):
            self._game_repository.update_observed_timestamp(game, datetime.now())
        return game

    def _update_required(self, last_observed_timestamp):
        return not last_observed_timestamp or last_observed_timestamp + self._update_period < datetime.now()


class UnobservedGamesInteractor:
    """ Removes games which have not been observed for a certain time period """
    def __init__(self, game_repository):
        self._game_repository = game_repository

    def remove_unobserved_games(self, unobserved_period=timedelta(hours=1)):
        """ Removes the unobserved games, returns identifiers of removed games """
        threshold = datetime.now() - unobserved_period
        games = self._game_repository.find_all_before_observed_timestamp(threshold)
        for game in games:
            self._game_repository.remove(game)
        return [game.identifier for game in games]


class GameRepository:
    """ Manages retrieval, deletion and updates of games

    Provides a domain-directed interface, detached from the intrinsics of the
    underlying data access. """
    def __init__(self, data_access):
        self._data_access = data_access

    def find_by_id(self, game_id, with_last_observed=False):
        game = self._data_access.load_game(game_id, with_last_observed=with_last_observed)
        if game is None:
            raise exceptions.GameNotFoundException
        return game

    def find_all_before_action_timestamp(self, timestamp):
        """ Retrieves games where the action timestamp is older than the given requested timestamp """
        return self._data_access.load_all_games_before_action_timestamp(timestamp)

    def find_all_before_observed_timestamp(self, timestamp):
        """ Retrieves games where the last-observed timestamp is older than the given requested timestamp """
        return self._data_access.load_all_games_before_observed_timestamp(timestamp)

    def update_action_timestamp(self, game, timestamp):
        self._data_access.update_action_timestamp(game.identifier, timestamp)

    def update_observed_timestamp(self, game, timestamp):
        self._data_access.update_observed_timestamp(game.identifier, timestamp)

    def update(self, game):
        self._data_access.update_game(game.identifier, game)

    def remove(self, game):
        self._data_access.delete_game(game.identifier)

    def register_game_created_listener(self, listener):
        self._data_access.register_game_created_listener(listener)

    def managed_gateway(self):
        """ Creates a database gateway as a context manager

        It should only be necessary to retrieve this in non-request contexts.
        """
        return DatabaseGateway(self._data_access.settings)
