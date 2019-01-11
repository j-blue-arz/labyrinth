""" Tests for Game of game.py """
from unittest.mock import Mock, patch, call
import pytest
from server.model.game import Game, BoardLocation, Player, PlayerAction, Board
from server.model.exceptions import PlayerNotFoundException, GameFullException


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


def test_add_and_remove_player_id_unique():
    """ Tests that after adding and removing players, the IDs are unique """
    game = Game(identifier=0)
    player_id1 = game.add_player(Player)
    player_id2 = game.add_player(Player)
    player_id3 = game.add_player(Player)
    game.remove_player(player_id2)
    player_id4 = game.add_player(Player)
    game.remove_player(player_id3)
    player_id5 = game.add_player(Player)
    game.remove_player(player_id1)
    player_id6 = game.add_player(Player)
    expected = set([player_id4, player_id5, player_id6])
    actual = set(player.identifier for player in game.players)
    assert actual == expected


@patch("model.computer.ComputerPlayer")
def test_change_player_calls_constructor_with_correct_arguments(mock_player_class):
    """ Tests change_player """
    game = Game(identifier=7)
    game.add_player(Player)
    player_id = game.add_player(Player)
    piece = game.get_player(player_id).piece
    board = game.get_player(player_id).board
    game.change_player(player_id, mock_player_class, param_name="value")
    mock_player_class.assert_called_once_with(
        identifier=player_id, game=game, param_name="value", piece=piece, board=board)


def test_change_player_keeps_id_and_piece_of_existing_player():
    """ Tests change_player """
    game = Game(identifier=7)
    player_id = game.add_player(Player)
    piece = game.players[0].piece
    game.change_player(player_id, Player)
    assert game.players[0].identifier == player_id
    assert game.players[0].piece == piece


def test_add_player_start_game_calls_methods_on_board():
    """ Tests add_player, start_game and Player """
    board = Board()
    turns = Mock()
    game = Game(identifier=0, board=board, turns=turns)
    with patch.object(board, 'create_piece',
                      wraps=board.create_piece) as board_create_piece:
        for _ in range(4):
            game.add_player(Player)
        game.start_game()
        expected_board_calls = [
            call.create_piece(),
            call.create_piece(),
            call.create_piece(),
            call.create_piece()]
        assert board_create_piece.mock_calls == expected_board_calls


def test_add_player_start_game_calls_methods_on_turns():
    """ Tests add_player, start_game and Player """
    board = Board()
    turns = Mock()
    game = Game(identifier=0, board=board, turns=turns)
    with patch.object(board, 'create_piece',
                      wraps=board.create_piece) as board_create_piece:
        for _ in range(4):
            game.add_player(Player)
        game.start_game()
        expected_turn_calls = [call.init(game.players)] + [call.start()]
        assert turns.mock_calls[-2:] == expected_turn_calls


@patch("model.game.Player")
def test_add_player_calls_constructor_with_correct_arguments(mock_player_class):
    """ Tests add_player """
    game = Game(identifier=7)
    game.add_player(mock_player_class, param_name="value")
    mock_player_class.assert_called_once()
    assert mock_player_class.call_args[0] == ()
    assert mock_player_class.call_args[1]["game"] == game
    assert mock_player_class.call_args[1]["param_name"] == "value"
    assert "identifier" in mock_player_class.call_args[1]


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

def test_get_enabled_shift_locations_without_previous_shift():
    """ Tests get_enabled_shift_locations where the previous shift is None """
    board = Board()
    game = Game(identifier=0, board=board)
    enabled_shift_locations = game.get_enabled_shift_locations()
    assert set(enabled_shift_locations) == set(board.INSERT_LOCATIONS)

def test_get_enabled_shift_locations_with_previous_shift():
    """ Tests get_enabled_shift_locations where the previous shift is (3, 0) """
    board = Board()
    game = Game(identifier=0, board=board)
    game.previous_shift_location = BoardLocation(3, 0)
    expected_disabled = BoardLocation(3, board.maze.MAZE_SIZE - 1)
    enabled_shift_locations = game.get_enabled_shift_locations()
    assert expected_disabled not in enabled_shift_locations

def test_player_reaches_objective_increase_score():
    """ Tests that the score on a player is increased once he reaches an objective """
    board = Mock()
    turns = Mock()
    turns.is_action_possible.return_value = True
    board.move.return_value = True
    game = Game(identifier=0, board=board, turns=turns)
    player_id = game.add_player(Player)
    old_score = game.get_player(player_id).score
    game.move(player_id, BoardLocation(0, 1))
    assert game.get_player(player_id).score == old_score + 1
