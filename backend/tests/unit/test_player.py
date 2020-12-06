""" Tests player of game.py """
from unittest.mock import Mock
from labyrinth.model.factories import create_board
from labyrinth.model.game import Player, Game


def given_game_and_player__when_set_game_on_player__creates_piece_for_player_on_board():
    board = create_board()
    game = Game(0, board=board)
    player = Player(0)

    player.set_game(game)

    assert player.piece in board.pieces


def test_register_in_turns():
    """ Tests that register_in_turns calls method in turns """
    turns = Mock()
    player = Player(1, 0)
    player.register_in_turns(turns)
    turns.add_player.assert_called_once_with(player)
