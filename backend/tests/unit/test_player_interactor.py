from unittest.mock import Mock

import pytest

import tests.unit.game_repository_mocks as game_repository_coach
from labyrinth.model import interactors
from labyrinth.model.game import Game, Turns, Player


@pytest.fixture()
def test_setup():
    def _setup(game_id, player_id):
        game = Game(game_id, turns=Turns())
        game.add_player(Player(player_id))
        game_repository = game_repository_coach.when_game_repository_find_by_id_then_return(game)
        game_repository.update = Mock()
        interactor = interactors.PlayerInteractor(game_repository=game_repository)
        return game, interactor

    return _setup


def test_change_name__changes_name_for_player(test_setup):
    game, interactor = test_setup(game_id=5, player_id=2)

    interactor.change_name(game_id=5, player_id=2, new_name="new name")

    assert game.get_player(2).player_name == "new name"
