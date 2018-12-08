""" Tests Piece of model.py """
from domain.model import Piece, MazeCard


def test_identifier():
    """ Tests identifier """
    piece = Piece(identifier=7)
    assert piece.identifier == 7


def test_has_reached_objective_is_true():
    """ Tests has_reached_objective """
    maze_card = MazeCard.generate_random()
    piece = Piece(identifier=7, maze_card=maze_card)
    piece.objective_maze_card = maze_card
    assert piece.has_reached_objective()


def test_has_reached_objective_is_false():
    """ Tests has_reached_objective """
    maze_card = MazeCard.generate_random()
    piece = Piece(identifier=7, maze_card=maze_card)
    piece.objective_maze_card = MazeCard.generate_random()
    assert not piece.has_reached_objective()
