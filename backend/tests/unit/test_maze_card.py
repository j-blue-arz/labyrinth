""" Tests for MazeCard of model.py """
import pytest
from domain.model import MazeCard
from domain.factories import create_random_maze_card


def test_generate_assigns_unique_ids():
    """ Tests generate_random """
    MazeCard.reset_ids()
    maze_card1 = MazeCard.create_instance(MazeCard.CORNER, 270)
    maze_card2 = MazeCard.create_instance(MazeCard.CORNER, 270)
    assert maze_card1.identifier != maze_card2.identifier


def test_generate_with_reset_ids_should_start_at_0():
    """ Tests generate_random with reset_ids """
    MazeCard.reset_ids()
    maze_card = MazeCard.create_instance(MazeCard.CORNER, 270)
    MazeCard.reset_ids()
    maze_card2 = MazeCard.create_instance(MazeCard.CORNER, 270)
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


def test_has_out_path_for_corner_with_rotation_90():
    """ Tests has_out_path """
    maze_card = MazeCard(0, MazeCard.CORNER, 90)
    assert not maze_card.has_out_path((-1, 0))
    assert maze_card.has_out_path((0, 1))
    assert maze_card.has_out_path((1, 0))
    assert not maze_card.has_out_path((0, -1))


def test_has_out_path_for_straight_with_rotation_270():
    """ Tests has_out_path """
    maze_card = MazeCard(0, MazeCard.STRAIGHT, 270)
    assert not maze_card.has_out_path((-1, 0))
    assert maze_card.has_out_path((0, 1))
    assert not maze_card.has_out_path((1, 0))
    assert maze_card.has_out_path((0, -1))


def test_out_paths_for_t_junct_with_rotation_180():
    """ Tests out_paths """
    maze_card = MazeCard(0, MazeCard.T_JUNCT, 180)
    assert (-1, 0) in maze_card.out_paths()
    assert (0, 1) not in maze_card.out_paths()
    assert (1, 0) in maze_card.out_paths()
    assert (0, -1) in maze_card.out_paths()


def test_out_paths_for_corner_with_rotation_0():
    """ Tests out_paths """
    maze_card = MazeCard(0, MazeCard.CORNER, 0)
    assert (-1, 0) in maze_card.out_paths()
    assert (0, 1) in maze_card.out_paths()
    assert (1, 0) not in maze_card.out_paths()
    assert (0, -1) not in maze_card.out_paths()
