from datetime import datetime, timedelta
from unittest.mock import Mock

from labyrinth.database import DatabaseGateway
from labyrinth.model import interactors
from labyrinth.model import factories
from labyrinth.model.game import Player


def setup_test():
    game = factories.create_game(game_id=5)
    player = Player(3)
    game.add_player(player)
    game.start_game()
    return game, player


def test_remove_overdue_players__with_one_blocking_player__removes_current_player():
    game, player = setup_test()
    game.remove_player = Mock()
    data_access = when_data_access_load_all_games_before_action_timestamp_then_return([game])

    interactor = interactors.OverduePlayerInteractor(data_access)
    interactor.remove_overdue_players()

    game.remove_player.assert_called_once_with(3)


def test_remove_overdue_players__with_player_just_removed__does_not_raise_exception():
    """ When the last remaining player was removed or has left the game,
    the update timestamp will stay at its last value. Then, the interactor must not try to remove a player.
    """
    game, player = setup_test()
    game.remove_player(player.identifier)
    data_access = when_data_access_load_all_games_before_action_timestamp_then_return([game])

    interactor = interactors.OverduePlayerInteractor(data_access)
    interactor.remove_overdue_players()


def test_interactor__when_game_notifies_turn_listeners__updates_player_action_timestamp():
    game, _ = setup_test()
    data_access = DatabaseGateway()
    data_access.update_action_timestamp = Mock()
    _ = interactors.OverduePlayerInteractor(data_access)
    data_access._notify_listeners(game)
    game._notify_turn_listeners()

    data_access.update_action_timestamp.assert_called_once_with(5, timestamp_close_to(datetime.now()))


def when_data_access_load_all_games_before_action_timestamp_then_return(games):
    data_access_mock = Mock(spec=DatabaseGateway)
    data_access_mock.load_all_games_before_action_timestamp = Mock(return_value=games)
    return data_access_mock


def timestamp_close_to(expected_timestamp, delta_ms=500):
    class Matcher:
        def __init__(self, expected_timestamp, delta_ms):
            self.expected_timestamp = expected_timestamp
            self.delta = timedelta(milliseconds=delta_ms)

        def __eq__(self, other_timestamp):
            matches = self.expected_timestamp - other_timestamp < self.delta
            if matches:
                return True
            else:
                raise AssertionError(f"expected: timestamp close to {self.expected_timestamp}, got {other_timestamp}")
    return Matcher(expected_timestamp, delta_ms)
