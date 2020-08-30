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
        game = self._load_game_or_throw(game_id)
        game.shift(player_id, shift_location, shift_rotation)
        self._game_repository.update_game(game_id, game)

    def perform_move(self, game_id, player_id, move_location):
        game = self._load_game_or_throw(game_id)
        game.move(player_id, move_location)
        self._game_repository.update_game(game_id, game)

    def _load_game_or_throw(self, game_id):
        game = self._game_repository.load_game(game_id)
        if game is None:
            raise exceptions.GameNotFoundException
        return game


class OverduePlayerInteractor:
    """ This interactor detects and removes players who are expected to perform an action,
    but have failed to do so for some period of time. """

    def __init__(self, game_repository):
        self._game_repository = game_repository
        game_repository.register_game_created_listener(self._on_game_creation)

    def remove_overdue_players(self, overdue_timedelta=timedelta(seconds=60)):
        """ Detects and removes players which are required to play next.

        Checks all currently running games.
        Players are automatically removed if it is their turn to play and
        they have not performed an action for a certain amount of time. """
        threshold = datetime.now() - overdue_timedelta
        games = self._game_repository.load_all_games_before_action_timestamp(threshold)
        for game in games:
            if game.players:
                player_id_to_remove = game.next_player().identifier
                game.remove_player(player_id_to_remove)
                self._game_repository.update_game(game.identifier, game)

    def _on_game_creation(self, game):
        game.register_turn_change_listener(self._turn_change_listener)

    def _turn_change_listener(self, game, player, next_action):
        self._game_repository.update_action_timestamp(game.identifier, datetime.now())
