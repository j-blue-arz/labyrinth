""" Tests for Game of model.py """
from unittest.mock import Mock, patch, call
import pytest
from domain.model import Game, BoardLocation, Player, PlayerAction
from domain.exceptions import PlayerNotFoundException, GameFullException


def test_add_get_player():
    """ Tests add_player and get_player """
    game = Game(identifier=0)
    player_id1 = game.add_player(Player)
    player_id2 = game.add_player(Player)
    assert game.get_player(player_id1).identifier == player_id1
    assert game.get_player(player_id2).identifier == player_id2


def test_get_player_raises_exception_for_unknown_id():
    """ Tests get_player """
    game = Game(identifier=0)
    with pytest.raises(PlayerNotFoundException):
        game.get_player(0)


def test_add_player_id_unique():
    """ Tests add_player """
    game = Game(identifier=0)
    ids = set()
    for _ in range(game.MAX_PLAYERS):
        ids.add(game.add_player(Player))
    assert len(ids) == game.MAX_PLAYERS


def test_start_game_with_four_players():
    """ Tests start_game and Player """
    board = Mock()
    turns = Mock()
    game = Game(identifier=0, board=board, turns=turns)
    for _ in range(4):
        game.add_player(Player)
    game.start_game()
    expected_board_calls = [
        call.clear_pieces(),
        call.create_piece(),
        call.create_piece(),
        call.create_piece(),
        call.create_piece()]
    assert board.mock_calls == expected_board_calls
    expected_turn_calls = [call.add_player(game.players[i]) for i in range(4)] + [call.start()]
    assert turns.mock_calls == expected_turn_calls


@patch("domain.model.Player")
def test_add_player_calls_constructor_with_correct_arguments(mock_player_class):
    """ Tests add_player """
    game = Game(identifier=7)
    game.add_player(mock_player_class, param_name="value")
    mock_player_class.assert_called_once_with(identifier=0, game_identifier=7, param_name="value")


def test_add_player_validation():
    """ Tests that adding more players than MAX_PLAYERS does not add another one """
    game = Game(identifier=0)
    for _ in range(game.MAX_PLAYERS):
        game.add_player(Player)
    with pytest.raises(GameFullException):
        game.add_player(Player)


def test_shift_raises_error_on_invalid_player_id():
    """ Tests shift validation """
    game = Game(identifier=0)
    player_id = game.add_player(Player)
    game.start_game()
    with pytest.raises(PlayerNotFoundException):
        game.shift(player_id + 1, BoardLocation(0, 1), 90)


def test_move_raises_error_on_invalid_player_id():
    """ Tests move validation """
    game = Game(identifier=0)
    player_id = game.add_player(Player)
    game.start_game()
    with pytest.raises(PlayerNotFoundException):
        game.move(player_id - 1, BoardLocation(5, 5))


def test_move_raises_error_on_invalid_turn():
    """ Tests turn validation """
    board = Mock()
    turns = Mock()
    turns.is_action_possible.return_value = False
    game = Game(identifier=0, board=board, turns=turns)
    player_id = game.add_player(Player)
    game.start_game()
    player = game.get_player(player_id)
    game.move(player_id, BoardLocation(0, 0))
    board.move.assert_not_called()
    turns.is_action_possible.assert_called_once_with(player, PlayerAction.MOVE_ACTION)


def test_move_does_not_raise_error_after_shift():
    """ Tests turn validation """
    board = Mock()
    turns = Mock()
    turns.is_action_possible.return_value = True
    game = Game(identifier=0, board=board, turns=turns)
    player_id = game.add_player(Player)
    game.start_game()
    player = game.get_player(player_id)
    game.move(player_id, BoardLocation(0, 0))
    board.move.assert_called_once()
    turns.is_action_possible.assert_called_once_with(player, PlayerAction.MOVE_ACTION)
