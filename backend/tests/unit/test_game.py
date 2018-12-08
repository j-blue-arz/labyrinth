""" Tests for Game of model.py """
import pytest
from unittest.mock import Mock
from domain.model import Game, BoardLocation, Turns
from domain.exceptions import PlayerNotFoundException, TurnActionViolationException


def test_add_check_player():
    """ Tests add_player and check_player """
    game = Game()
    player_id1 = game.add_player()
    player_id2 = game.add_player()
    game.check_player(player_id1)
    game.check_player(player_id2)


def test_accepts_players():
    """ Tests accepts_players """
    game = Game()
    for _ in range(game.MAX_PLAYERS):
        assert game.accepts_players()
        game.add_player()
    assert not game.accepts_players()


def test_add_player_validation():
    """ Tests that adding more players than MAX_PLAYERS does not add another one """
    game = Game()
    while game.accepts_players():
        game.add_player()
    assert game.add_player() is None


def test_shift_raises_error_on_invalid_player_id():
    """ Tests shift validation """
    game = Game()
    player_id = game.add_player()
    game.init_game()
    with pytest.raises(PlayerNotFoundException):
        game.shift(player_id + 1, BoardLocation(0, 1), 90)


def test_move_raises_error_on_invalid_player_id():
    """ Tests move validation """
    game = Game()
    player_id = game.add_player()
    game.init_game()
    with pytest.raises(PlayerNotFoundException):
        game.move(player_id - 1, BoardLocation(5, 5))


def test_move_raises_error_on_invalid_turn():
    """ Tests turn validation """
    board = Mock()
    game = Game(board)
    player_id = game.add_player()
    game.init_game()
    with pytest.raises(TurnActionViolationException):
        game.move(player_id, BoardLocation(0, 0))
    board.move.assert_not_called()

def test_move_does_not_raise_error_after_shift():
    """ Tests turn validation """
    board = Mock()
    game = Game(board)
    player_id = game.add_player()
    game.init_game()
    game.turns.perform_action(player_id, Turns.SHIFT_ACTION)
    game.move(player_id, BoardLocation(0, 0))
    board.move.assert_called_once()