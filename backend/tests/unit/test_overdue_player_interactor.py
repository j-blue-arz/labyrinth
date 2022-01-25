from datetime import datetime
from unittest.mock import Mock

from labyrinth.database import DatabaseGateway
from labyrinth.model import interactors
from labyrinth.model import factories
from labyrinth.model.game import Player
from tests.unit import matchers

logger = Mock()


def setup_test(players=None):
    game = factories.create_game(game_id=5)
    for player in players:
        game.add_player(player)
    logger.reset_mock()
    return game


def test_remove_overdue_players__with_one_blocking_player__removes_current_player():
    game = setup_test(players=[Player(3), Player(4)])
    game.remove_player = Mock()
    game_repository = when_game_repository_find_all_before_action_timestamp_then_return([game])

    interactor = interactors.OverduePlayerInteractor(game_repository, logger)
    interactor.remove_overdue_players()

    game.remove_player.assert_called_once_with(3)
    logger.remove_player.assert_called_once()


def test_remove_overdue_players__with_player_just_removed__does_not_raise_exception():
    """ When the last remaining player was removed or has left the game,
    the update timestamp will stay at its last value. Then, the interactor must not try to remove a player.
    """
    game = setup_test(players=[Player(3)])
    game.remove_player(3)
    game_repository = when_game_repository_find_all_before_action_timestamp_then_return([game])

    interactor = interactors.OverduePlayerInteractor(game_repository, logger)
    interactor.remove_overdue_players()


def test_interactor__when_game_notifies_turn_listeners__updates_player_action_timestamp():
    game = setup_test(players=[Player(3), Player(4)])
    data_access = DatabaseGateway(settings={"DATABASE": "foo"})
    game_repository = interactors.GameRepository(data_access)
    game_repository.update_action_timestamp = Mock()
    _ = interactors.OverduePlayerInteractor(game_repository, logger)
    data_access._notify_listeners(game)
    game._notify_turn_listeners()

    game_repository.update_action_timestamp.assert_called_once_with(game, matchers.timestamp_close_to(datetime.now()))


def when_game_repository_find_all_before_action_timestamp_then_return(games):
    game_repository_mock = Mock(spec=interactors.GameRepository)
    game_repository_mock.find_all_before_action_timestamp = Mock(return_value=games)
    return game_repository_mock
