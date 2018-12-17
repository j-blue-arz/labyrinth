""" Tests Piece of model.py """
from domain.model import Piece
from domain.factories import create_random_maze_card


def test_has_reached_objective_is_true():
    """ Tests has_reached_objective """
    maze_card = create_random_maze_card()
    piece = Piece(maze_card=maze_card)
    piece.objective_maze_card = maze_card
    assert piece.has_reached_objective()


def test_has_reached_objective_is_false():
    """ Tests has_reached_objective """
    maze_card = create_random_maze_card()
    piece = Piece(maze_card=maze_card)
    piece.objective_maze_card = create_random_maze_card()
    assert not piece.has_reached_objective()
