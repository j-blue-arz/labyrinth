from datetime import datetime

from labyrinth.model import exceptions


class PlayerActionInteractor:
    def __init__(self, game_repository):
        self._game_repository = game_repository

    def perform_shift(self, game_id, player_id, shift_location, shift_rotation):
        game = self._load_game_or_throw(game_id)
        game.shift(player_id, shift_location, shift_rotation)
        self._game_repository.update_game(game_id, game)
        self._game_repository.update_action_timestamp(game_id, datetime.now())

    def perform_move(self, game_id, player_id, move_location):
        game = self._load_game_or_throw(game_id)
        game.move(player_id, move_location)
        self._game_repository.update_game(game_id, game)
        self._game_repository.update_action_timestamp(game_id, datetime.now())

    def _load_game_or_throw(self, game_id):
        game = self._game_repository.load_game(game_id)
        if game is None:
            raise exceptions.GameNotFoundException
        return game
