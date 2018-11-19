""" Tests for MazeCard of model.py """
import pytest
from model import MazeCard

def test_generate_assigns_unique_ids():
    """ Tests generate_random """
    MazeCard.reset_ids()
    maze_card1 = MazeCard.generate_random()
    maze_card2 = MazeCard.generate_random()
    assert maze_card1.identifier != maze_card2.identifier

def test_generate_with_reset_ids_should_start_at_0():
    """ Tests generate_random with reset_ids """
    MazeCard.reset_ids()
    maze_card = MazeCard.generate_random()
    MazeCard.reset_ids()
    maze_card2 = MazeCard.generate_random()
    assert maze_card.identifier == maze_card2.identifier

def test_rotation_should_be_settable():
    """ Tests rotation getter and setter """
    maze_card = MazeCard()
    maze_card.rotation = 90
    assert maze_card.rotation == 90

def test_rotation_setter_should_throw_for_invalid_rotation():
    """ Tests rotation setter """
    maze_card = MazeCard()
    with pytest.raises(ValueError):
        maze_card.rotation = 80
    