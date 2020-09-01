""" Tests UnobservedGamesInteractor.

Uses mocked GameRepository
"""

from datetime import datetime, timedelta
from unittest.mock import Mock

from labyrinth.model import factories
from labyrinth.model import interactors


def test_remove_unobserved__after_unobserved_period__deletes_game():
    game1 = factories.create_game(game_id=5)
    game2 = factories.create_game(game_id=7)
    games_by_timestamp = {ago(hours=2): game1, ago(minutes=30): game2}
    game_repository = when_game_repository__find_all_before_observed_timestamp__then_answer(games_by_timestamp)

    interactors.UnobservedGamesInteractor(game_repository=game_repository)
    interactors.remove_unobserved_games(unobserved_period=timedelta(hours=1))

    game_repository.remove.assert_called_once_with(game1)


def when_game_repository__find_all_before_observed_timestamp__then_answer(games_by_timestamp):
    game_repository_mock = Mock(spec=interactors.GameRepository)

    def return_games_before(requested_timestamp):
        return [game for timestamp, game in games_by_timestamp.items() if timestamp < requested_timestamp]

    game_repository_mock.find_all_before_observed_timestamp = Mock(side_effect=return_games_before)
    return game_repository_mock


def ago(**kwargs):
    return datetime.now() - timedelta(kwargs)
