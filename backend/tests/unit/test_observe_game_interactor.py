""" Tests ObserveGameInteractor. Uses real GameRepository instead of mock."""
from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest

from labyrinth.database import DatabaseGateway
from labyrinth.model import exceptions
from labyrinth.model import factories
from labyrinth.model import interactors
from tests.unit import matchers


def setup_test(game_id=7, last_observed_timestamp=datetime.now()):
    game = factories.create_game(game_id=game_id)
    data_access = when_data_access__load_game__then_return(game, last_observed_timestamp)
    game_repository = interactors.GameRepository(data_access)

    return game, game_repository, data_access


def test_retrieve_game__returns_game():
    game, game_repository, _ = setup_test(game_id=7)
    interactor = interactors.ObserveGameInteractor(game_repository)

    retrieved_game = interactor.retrieve_game(7)

    assert retrieved_game == game


def test_retrieve_game__with_game_not_existing__raise_exception():
    game, game_repository, _ = setup_test(game_id=7)
    interactor = interactors.ObserveGameInteractor(game_repository)

    with pytest.raises(exceptions.GameNotFoundException):
        interactor.retrieve_game(3)


def test_retrieve_game__after_update_period__updates_last_observed_timestamp():
    last_observed_timestamp = datetime.now() - timedelta(seconds=120)
    game, game_repository, data_access = setup_test(last_observed_timestamp=last_observed_timestamp)

    interactor = interactors.ObserveGameInteractor(game_repository=game_repository, update_period=timedelta(seconds=60))
    interactor.retrieve_game(7)

    close_to_now = matchers.timestamp_close_to(datetime.now())
    data_access.update_observed_timestamp.assert_called_once_with(game.identifier, close_to_now)


def test_retrieve_game__before_update_period__does_not_update_last_observed_timestamp():
    last_observed_timestamp = datetime.now() - timedelta(seconds=10)
    game, game_repository, data_access = setup_test(last_observed_timestamp=last_observed_timestamp)

    interactor = interactors.ObserveGameInteractor(game_repository=game_repository, update_period=timedelta(seconds=60))
    interactor.retrieve_game(7)

    data_access.update_observed_timestamp.assert_not_called()


def test_retrieve_game__with_nonexisting_last_observed_timestamp__updates_last_observed_timestamp():
    game, game_repository, data_access = setup_test(last_observed_timestamp=None)

    interactor = interactors.ObserveGameInteractor(game_repository=game_repository, update_period=timedelta(seconds=60))
    interactor.retrieve_game(7)

    close_to_now = matchers.timestamp_close_to(datetime.now())
    data_access.update_observed_timestamp.assert_called_once_with(game.identifier, close_to_now)


def when_data_access__load_game__then_return(game, last_observed=datetime.now()):
    data_access_mock = Mock(spec=DatabaseGateway)
    game_id = game.identifier

    def return_game(requested_game_id, with_last_observed):
        if requested_game_id == game_id:
            if with_last_observed:
                return game, last_observed
            else:
                return game
        else:
            return None

    data_access_mock.load_game = Mock(side_effect=return_game)
    data_access_mock.update_observed_timestamp = Mock()
    return data_access_mock
