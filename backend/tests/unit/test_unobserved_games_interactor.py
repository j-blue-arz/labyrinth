""" Tests UnobservedGamesInteractor.

Uses mocked GameRepository
"""

from datetime import datetime, timedelta
from unittest.mock import Mock

from labyrinth.model import factories
from labyrinth.model import interactors
from labyrinth.model.game import Player

logger = Mock()


def test_remove_unobserved__after_unobserved_period__deletes_game():
    game1 = factories.create_game(game_id=5)
    game2 = factories.create_game(game_id=7)
    games_by_timestamp = {ago(hours=2): game1, ago(minutes=30): game2}
    game_repository = when_game_repository__find_all_before_observed_timestamp__then_answer(games_by_timestamp)

    interactor = interactors.UnobservedGamesInteractor(game_repository=game_repository, logger=logger)
    interactor.remove_unobserved_games(unobserved_period=timedelta(hours=1))

    game_repository.remove.assert_called_once_with(game1)


def test_remove_unobserved__with_two_bots_remaining__logs_player_removal_with_correct_number():
    game = factories.create_game()
    game.add_player(Player(3))
    game.add_player(Player(7))
    game_repository = when_game_repository__find_all_before_observed_timestamp__then_answer({ago(hours=2): game})

    interactor = interactors.UnobservedGamesInteractor(game_repository=game_repository, logger=logger)
    logger.reset_mock()
    interactor.remove_unobserved_games(unobserved_period=timedelta(hours=1))

    assert logger.remove_player.call_count == 2
    player_id_args = {arg[0][0] for arg in logger.remove_player.call_args_list}
    assert_equal_in_any_order([3, 7], player_id_args)

    num_player_args = [arg[1]["num_players"] for arg in logger.remove_player.call_args_list]
    assert num_player_args == [1, 0]


def when_game_repository__find_all_before_observed_timestamp__then_answer(games_by_timestamp):
    game_repository_mock = Mock(spec=interactors.GameRepository)

    def return_games_before(requested_timestamp):
        return [game for timestamp, game in games_by_timestamp.items() if timestamp < requested_timestamp]

    game_repository_mock.find_all_before_observed_timestamp = Mock(side_effect=return_games_before)
    return game_repository_mock


def ago(**kwargs):
    return datetime.now() - timedelta(**kwargs)


def assert_equal_in_any_order(list1, list2):
    assert len(list1) == len(list2)
    diff = set(list1) ^ set(list2)
    assert not diff
