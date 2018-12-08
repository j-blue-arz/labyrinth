""" Tests Turns of model.py """
import pytest
from domain.exceptions import TurnActionViolationException
from domain.model import Turns


def test_next_player_action_should_be_none_without_players():
    """ Tests next_player_action """
    turns = Turns()
    assert turns.next_player_action() is None

def test_next_player_action_with_one_player_should_be_shift():
    """ Tests next_player_action """
    player = 7
    turns = Turns([player])
    assert turns.next_player_action() == (player, Turns.SHIFT_ACTION)

def test_next_player_action_after_perform_shift_should_be_move():
    """ Tests next_player_action and perform_action """
    player = 7
    turns = Turns([player])
    turns.perform_action(player, Turns.SHIFT_ACTION)
    assert turns.next_player_action() == (player, Turns.MOVE_ACTION)


def test_perform_invalid_action_should_raise():
    """ Tests perform_action """
    player1, player2 = 7, 11
    turns = Turns([player1, player2])
    with pytest.raises(TurnActionViolationException):
        turns.perform_action(player2, Turns.SHIFT_ACTION)

def test_perform_invalid_action_does_not_alter_turns():
    """ Tests perform_action """
    player1, player2 = 7, 11
    turns = Turns([player1, player2])
    with pytest.raises(TurnActionViolationException):
        turns.perform_action(player2, Turns.SHIFT_ACTION)
    turns.perform_action(player1, Turns.SHIFT_ACTION)
    turns.perform_action(player1, Turns.MOVE_ACTION)
    turns.perform_action(player2, Turns.SHIFT_ACTION)
    with pytest.raises(TurnActionViolationException):
        turns.perform_action(player2, Turns.SHIFT_ACTION)

def test_is_action_possible_with_next_action():
    """ Tests is_action_possible and constructor parameter next_action """
    players = [9, 0, 3]
    turns = Turns(players, next_action=(players[2], Turns.MOVE_ACTION))
    assert not turns.is_action_possible(players[0], Turns.SHIFT_ACTION)
    assert not turns.is_action_possible(players[1], Turns.SHIFT_ACTION)
    assert turns.is_action_possible(players[2], Turns.MOVE_ACTION)
    turns.perform_action(players[2], Turns.MOVE_ACTION)
    assert turns.is_action_possible(players[0], Turns.SHIFT_ACTION)
    assert not turns.is_action_possible(players[1], Turns.SHIFT_ACTION)
    turns.perform_action(players[0], Turns.SHIFT_ACTION)
    turns.perform_action(players[0], Turns.MOVE_ACTION)
    assert not turns.is_action_possible(players[0], Turns.SHIFT_ACTION)
    assert turns.is_action_possible(players[1], Turns.SHIFT_ACTION)

def test_is_action_possible_with_complete_cycle():
    """ Tests is_action_possible """
    players = [2, 1]
    turns = Turns(players)
    assert turns.is_action_possible(players[0], Turns.SHIFT_ACTION)
    assert not turns.is_action_possible(players[0], Turns.MOVE_ACTION)
    assert not turns.is_action_possible(players[1], Turns.SHIFT_ACTION)
    assert not turns.is_action_possible(players[1], Turns.MOVE_ACTION)
    turns.perform_action(players[0], Turns.SHIFT_ACTION)
    turns.perform_action(players[0], Turns.MOVE_ACTION)
    turns.perform_action(players[1], Turns.SHIFT_ACTION)
    assert not turns.is_action_possible(players[0], Turns.SHIFT_ACTION)
    assert not turns.is_action_possible(players[0], Turns.MOVE_ACTION)
    assert not turns.is_action_possible(players[1], Turns.SHIFT_ACTION)
    assert turns.is_action_possible(players[1], Turns.MOVE_ACTION)
    turns.perform_action(players[1], Turns.MOVE_ACTION)
    assert turns.is_action_possible(players[0], Turns.SHIFT_ACTION)
    assert not turns.is_action_possible(players[0], Turns.MOVE_ACTION)
    assert not turns.is_action_possible(players[1], Turns.SHIFT_ACTION)
    assert not turns.is_action_possible(players[1], Turns.MOVE_ACTION)
    turns.perform_action(players[0], Turns.SHIFT_ACTION)
