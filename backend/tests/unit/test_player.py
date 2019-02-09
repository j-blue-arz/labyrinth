""" Tests player of game.py """
from unittest.mock import MagicMock
from server.model.game import Player, Piece
from server.model.factories import create_random_maze_card


def test_set_board():
    """ Tests that set_board asks the board for a piece """
    board = MagicMock()
    piece = Piece(0, create_random_maze_card)
    board.create_piece.return_value = piece
    player = Player(1, 0)
    player.set_board(board)
    board.create_piece.assert_called_once_with()
    assert player.piece is piece


def test_register_in_turns():
    """ Tests that register_in_turns calls method in turns """
    turns = MagicMock()
    player = Player(1, 0)
    player.register_in_turns(turns)
    turns.add_player.assert_called_once_with(player)
