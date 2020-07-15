""" Tests Turns of game.py """
from unittest.mock import Mock
import pytest
from app.model.exceptions import TurnActionViolationException
from app.model.game import Turns, PlayerAction, Player


def test_next_player_action_should_be_none_without_players():
    """ Tests next_player_action """
    turns = Turns()
    assert turns.next_player_action() is None


def test_next_player_action_with_one_player_should_be_shift():
    """ Tests next_player_action """
    player = Player(7, 0)
    turns = Turns([player])
    assert turns.next_player_action() == PlayerAction(player, PlayerAction.SHIFT_ACTION)


def test_next_player_action_after_perform_shift_should_be_move():
    """ Tests next_player_action and perform_action """
    player = Player(7, 0)
    turns = Turns([player])
    turns.perform_action(player, PlayerAction.SHIFT_ACTION)
    assert turns.next_player_action() == PlayerAction(player, PlayerAction.MOVE_ACTION)


def test_perform_invalid_action_should_raise():
    """ Tests perform_action """
    player1, player2 = Player(7, 0), Player(11, 0)
    turns = Turns([player1, player2])
    with pytest.raises(TurnActionViolationException):
        turns.perform_action(player2, PlayerAction.SHIFT_ACTION)


def test_perform_invalid_action_does_not_alter_turns():
    """ Tests perform_action """
    player1, player2 = Player(7, 0), Player(11, 0)
    turns = Turns([player1, player2])
    with pytest.raises(TurnActionViolationException):
        turns.perform_action(player2, PlayerAction.SHIFT_ACTION)
    turns.perform_action(player1, PlayerAction.SHIFT_ACTION)
    turns.perform_action(player1, PlayerAction.MOVE_ACTION)
    turns.perform_action(player2, PlayerAction.SHIFT_ACTION)
    with pytest.raises(TurnActionViolationException):
        turns.perform_action(player2, PlayerAction.SHIFT_ACTION)


def test_is_action_possible_with_next_action():
    """ Tests is_action_possible and constructor parameter next_action """
    players = [Player(id, 0) for id in [9, 0, 3]]
    turns = Turns(players, next_action=PlayerAction(players[2], PlayerAction.MOVE_ACTION))
    assert not turns.is_action_possible(players[0], PlayerAction.SHIFT_ACTION)
    assert not turns.is_action_possible(players[1], PlayerAction.SHIFT_ACTION)
    assert turns.is_action_possible(players[2], PlayerAction.MOVE_ACTION)
    turns.perform_action(players[2], PlayerAction.MOVE_ACTION)
    assert turns.is_action_possible(players[0], PlayerAction.SHIFT_ACTION)
    assert not turns.is_action_possible(players[1], PlayerAction.SHIFT_ACTION)
    turns.perform_action(players[0], PlayerAction.SHIFT_ACTION)
    turns.perform_action(players[0], PlayerAction.MOVE_ACTION)
    assert not turns.is_action_possible(players[0], PlayerAction.SHIFT_ACTION)
    assert turns.is_action_possible(players[1], PlayerAction.SHIFT_ACTION)


def test_is_action_possible_with_complete_cycle():
    """ Tests is_action_possible """
    players = [Player(id, 0) for id in [2, 1]]
    turns = Turns(players)
    assert turns.is_action_possible(players[0], PlayerAction.SHIFT_ACTION)
    assert not turns.is_action_possible(players[0], PlayerAction.MOVE_ACTION)
    assert not turns.is_action_possible(players[1], PlayerAction.SHIFT_ACTION)
    assert not turns.is_action_possible(players[1], PlayerAction.MOVE_ACTION)
    turns.perform_action(players[0], PlayerAction.SHIFT_ACTION)
    turns.perform_action(players[0], PlayerAction.MOVE_ACTION)
    turns.perform_action(players[1], PlayerAction.SHIFT_ACTION)
    assert not turns.is_action_possible(players[0], PlayerAction.SHIFT_ACTION)
    assert not turns.is_action_possible(players[0], PlayerAction.MOVE_ACTION)
    assert not turns.is_action_possible(players[1], PlayerAction.SHIFT_ACTION)
    assert turns.is_action_possible(players[1], PlayerAction.MOVE_ACTION)
    turns.perform_action(players[1], PlayerAction.MOVE_ACTION)
    assert turns.is_action_possible(players[0], PlayerAction.SHIFT_ACTION)
    assert not turns.is_action_possible(players[0], PlayerAction.MOVE_ACTION)
    assert not turns.is_action_possible(players[1], PlayerAction.SHIFT_ACTION)
    assert not turns.is_action_possible(players[1], PlayerAction.MOVE_ACTION)
    turns.perform_action(players[0], PlayerAction.SHIFT_ACTION)


def test_start_calls_callback_if_present():
    """ Tests start for player with callback """
    turns = Turns()
    player = Player(7, 0)
    callback = Mock()
    turns.add_player(player, turn_callback=callback)
    callback.assert_not_called()
    turns.start()
    callback.assert_called_once()


def test_perform_action_calls_callback_if_present():
    """ Tests perform_action for player with callback """
    turns = Turns()
    player1 = Mock()
    player2 = Mock()
    turns.add_player(player1)
    turns.add_player(player2, turn_callback=player2.callback)
    turns.start()
    turns.perform_action(player1, PlayerAction.SHIFT_ACTION)
    player2.callback.assert_not_called()
    turns.perform_action(player1, PlayerAction.MOVE_ACTION)
    player2.callback.assert_called_once()
    player2.callback.reset_mock()
    turns.perform_action(player2, PlayerAction.SHIFT_ACTION)
    player2.callback.assert_not_called()


def test_callback_with_one_player():
    """ Tests that the callback on a player is called after each move, even if he plays alone """
    turns = Turns()
    player1 = Mock()
    turns.add_player(player1, turn_callback=player1.callback)
    turns.start()
    player1.callback.assert_called_once()
    player1.callback.reset_mock()
    turns.perform_action(player1, PlayerAction.SHIFT_ACTION)
    turns.perform_action(player1, PlayerAction.MOVE_ACTION)
    player1.callback.assert_called_once()


def test_removed_player_no_callback_called():
    """ Tests remove_player """
    turns = Turns()
    player1 = Mock()
    player2 = Mock()
    turns.add_player(player1, turn_callback=player1.callback)
    turns.add_player(player2, turn_callback=player2.callback)
    turns.start()
    turns.remove_player(player2)
    turns.perform_action(player1, PlayerAction.SHIFT_ACTION)
    turns.perform_action(player1, PlayerAction.MOVE_ACTION)
    player2.callback.assert_not_called()


def test_remove_first_player_next_player_action_should_be_remaining_player():
    """ Tests after removing the first of two players, next_player_action() should not return None """
    turns = Turns()
    player1, player2 = Mock(), Mock()
    turns.add_player(player1, turn_callback=player1.callback)
    turns.add_player(player2, turn_callback=player2.callback)
    turns.start()
    turns.remove_player(player1)
    assert turns.next_player_action() is not None
    assert turns.next_player_action().player is player2
    player2.callback.assert_called_once()


def test_remove_second_player_next_player_action_should_be_remaining_player():
    """ Tests after removing the second of two players, next_player_action() should not return None """
    turns = Turns()
    player1, player2 = Mock(), Mock()
    turns.add_player(player1, turn_callback=player1.callback)
    turns.add_player(player2, turn_callback=player2.callback)
    turns.start()
    turns.perform_action(player1, PlayerAction.SHIFT_ACTION)
    turns.perform_action(player1, PlayerAction.MOVE_ACTION)
    player1.callback.reset_mock()
    turns.remove_player(player2)
    assert turns.next_player_action() is not None
    assert turns.next_player_action().player is player1
    player1.callback.assert_called_once()
