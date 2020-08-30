from unittest.mock import Mock

import pytest

from labyrinth.database import DatabaseGateway
from labyrinth.model import interactors
from labyrinth.model.exceptions import InvalidShiftLocationException, TurnActionViolationException
from labyrinth.model.game import BoardLocation, Game, Player


@pytest.fixture()
def test_setup():
    def _setup():
        game = Game(5)
        data_access_mock = when_data_access_load_game_then_return(game)
        data_access_mock.update_game = Mock()
        interactor = interactors.PlayerActionInteractor(game_repository=data_access_mock)
        return game, interactor, data_access_mock

    return _setup


def test_perform_shift__calls_shift_on_game(test_setup):
    game, player_action_interactor, _ = test_setup()
    game.shift = Mock()

    player_action_interactor.perform_shift(game_id=5, player_id=7,
                                           shift_location=BoardLocation(1, 2), shift_rotation=90)

    game.shift.assert_called_once_with(7, BoardLocation(1, 2), 90)


def test_perform_shift__updates_game_with_new_state(test_setup):
    game, player_action_interactor, data_access = test_setup()
    when_game_shift_then_set_previous_shift_location(game)

    player_action_interactor.perform_shift(game_id=5, player_id=7,
                                           shift_location=BoardLocation(1, 2), shift_rotation=90)

    data_access.update_game.assert_called_once_with(5, game_with_previous_shift_location(BoardLocation(1, 2)))


def test_perform_shift__when_exception_raised_by_game__then_no_update(test_setup):
    game, player_action_interactor, data_access = test_setup()
    when_game_shift_then_raise(game, InvalidShiftLocationException())
    with pytest.raises(InvalidShiftLocationException):
        player_action_interactor.perform_shift(game_id=5, player_id=7,
                                               shift_location=BoardLocation(1, 2), shift_rotation=90)

    data_access.update_game.assert_not_called()


def test_perform_move__calls_move_on_game(test_setup):
    game, player_action_interactor, _ = test_setup()
    game.move = Mock()

    player_action_interactor.perform_move(game_id=5, player_id=7, move_location=BoardLocation(3, 7))

    game.move.assert_called_once_with(7, BoardLocation(3, 7))


def test_perform_move__updates_game_with_new_state(test_setup):
    game, player_action_interactor, data_access = test_setup()
    game.add_player(Player(7))
    when_game_move_then_increase_player_score(game)

    player_action_interactor.perform_move(game_id=5, player_id=7, move_location=BoardLocation(3, 7))

    data_access.update_game.assert_called_once_with(5, game_with_player_score(1))


def test_perform_move__when_exception_raised_by_game__then_no_update(test_setup):
    game, player_action_interactor, data_access = test_setup()
    when_game_move_then_raise(game, TurnActionViolationException())
    with pytest.raises(TurnActionViolationException):
        player_action_interactor.perform_move(game_id=5, player_id=7, move_location=BoardLocation(3, 7))

    data_access.update_game.assert_not_called()


def game_with_previous_shift_location(expected_location):
    class Matcher:
        def __init__(self, expected_location):
            self.expected_location = expected_location

        def __eq__(self, game):
            return game.previous_shift_location == self.expected_location
    return Matcher(expected_location)


def game_with_player_score(expected_score):
    class Matcher:
        def __init__(self, expected_score):
            self.expected_score = expected_score

        def __eq__(self, game):
            score = game.players[0].score
            if self.expected_score == score:
                return True
            else:
                raise AssertionError(f"expected: game with player score of {self.expected_score}, got {score}")
    return Matcher(expected_score)


def when_game_shift_then_raise(game, error):
    game.shift = Mock(side_effect=error)


def when_game_move_then_raise(game, error):
    game.move = Mock(side_effect=error)


def when_game_shift_then_set_previous_shift_location(game):
    def mock_shift(player_id, new_leftover_location, leftover_rotation):
        game.previous_shift_location = new_leftover_location

    game.shift = Mock(side_effect=mock_shift)


def when_game_move_then_increase_player_score(game):
    def mock_move(player_id, move_location):
        game.players[0].score += 1

    game.move = Mock(side_effect=mock_move)


def when_data_access_load_game_then_return(game):
    data_access_mock = Mock(spec=DatabaseGateway)
    game_id = game.identifier

    def return_game(requested_game_id):
        if requested_game_id == game_id:
            return game
        else:
            return None

    data_access_mock.load_game = Mock(side_effect=return_game)
    return data_access_mock
