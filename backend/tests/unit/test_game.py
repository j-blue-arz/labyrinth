""" Tests for Game of model.py """
import pytest
from labyrinth.model import Game, BoardLocation

def test_add_find_player():
    """ Tests add_player and find_player """
    game = Game()
    player_id1 = game.add_player()
    player_id2 = game.add_player()
    assert game.find_player(player_id1).identifier == player_id1
    assert game.find_player(player_id2).identifier == player_id2

def test_accepts_players():
    """ Tests accepts_players """
    game = Game()
    for _ in range(game.MAX_PLAYERS):
        assert game.accepts_players()
        game.add_player()
    assert not game.accepts_players()

def test_move_updates_players_maze_card_correctly():
    """ Tests move """
    game = Game()
    player_id = game.add_player()
    game.init_game()
    game.move(player_id, BoardLocation(2, 3))
    assert game.board[BoardLocation(2, 3)] == game.find_player(player_id).maze_card

def test_shift_updates_old_leftover_rotation():
    """ Tests shift """
    game = Game()
    player_id = game.add_player()
    game.init_game()
    old_leftover = game.leftover_card
    game.shift(player_id, BoardLocation(0, 1), 270)
    assert old_leftover.rotation == 270

def test_shift_updates_new_leftover():
    """ Tests shift """
    game = Game()
    player_id = game.add_player()
    game.init_game()
    pushed_out = game.board[BoardLocation(game.board.BOARD_SIZE - 1, 1)]
    game.shift(player_id, BoardLocation(0, 1), 270)
    assert pushed_out == game.leftover_card

def test_shift_updates_players_on_pushed_out_card():
    """ Tests shift """
    game = Game()
    player_id = game.add_player()
    player = game.find_player(player_id)
    game.init_game()
    pushed_card = game.leftover_card
    player.maze_card = game.board[BoardLocation(0, 3)]
    game.shift(player_id, BoardLocation(game.board.BOARD_SIZE-1, 3), 90)
    assert player.maze_card == pushed_card

def test_add_player_validation():
    """ Tests that adding more players than MAX_PLAYERS does not add another one """
    game = Game()
    while game.accepts_players():
        game.add_player()
    assert game.add_player() is None

def test_shift_raises_error_on_invalid_location():
    """ Tests shift validation """
    game = Game()
    player_id = game.add_player()
    game.init_game()
    with pytest.raises(ValueError):
        game.shift(player_id, BoardLocation(0, 0), 90)

def test_shift_raises_error_on_invalid_rotation():
    """ Tests shift validation """
    game = Game()
    player_id = game.add_player()
    game.init_game()
    with pytest.raises(ValueError):
        game.shift(player_id, BoardLocation(0, 1), 70)

def test_shift_raises_error_on_invalid_player_id():
    """ Tests shift validation """
    game = Game()
    player_id = game.add_player()
    game.init_game()
    with pytest.raises(ValueError):
        game.shift(player_id + 1, BoardLocation(0, 1), 90)

def test_move_raises_error_on_invalid_location():
    """ Tests move validation """
    game = Game()
    player_id = game.add_player()
    game.init_game()
    with pytest.raises(ValueError):
        game.move(player_id, BoardLocation(-1, -1))


def test_move_raises_error_on_invalid_player_id():
    """ Tests move validation """
    game = Game()
    player_id = game.add_player()
    game.init_game()
    with pytest.raises(ValueError):
        game.move(player_id - 1, BoardLocation(5, 5))
