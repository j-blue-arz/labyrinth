""" Game-related use case interactors.

Also defines the GameRepository.
"""

from datetime import datetime, timedelta

from labyrinth.model import exceptions


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


class OverduePlayerInteractor:
    """ This interactor detects and removes players who are expected to perform an action,
    but have failed to do so for some period of time. """

    def __init__(self, game_repository):
        self._game_repository = game_repository
        self._game_repository.register_game_created_listener(self._on_game_creation)

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

    def _on_game_creation(self, game):
        game.register_turn_change_listener(self._turn_change_listener)

    def _turn_change_listener(self, game, player, next_action):
        self._game_repository.update_action_timestamp(game, datetime.now())


class GameRepository:
    """ Object to retrieve game instances.

    Providing a domain-directed interface, detached from the intrinsics of the
    underlying data access. """
    def __init__(self, data_access):
        self._data_access = data_access

    def update(self, game):
        self._data_access.update_game(game.identifier, game)

    def find_by_id(self, game_id):
        game = self._data_access.load_game(game_id)
        if game is None:
            raise exceptions.GameNotFoundException
        return game

    def find_all_before_action_timestamp(self, timestamp):
        """ Retrieves games where the action timestamp is older than the given requested timestamp """
        return self._data_access.load_all_games_before_action_timestamp(timestamp)

    def update_action_timestamp(self, game, timestamp):
        self._data_access.update_action_timestamp(game.identifier, timestamp)

    def register_game_created_listener(self, listener):
        self._data_access.register_game_created_listener(listener)
