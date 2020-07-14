""" Tests for MazeCard of game.py """
import pytest
from server.model.game import MazeCard


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
    """ Tests has_rotated_out_path """
    maze_card = MazeCard(0, MazeCard.CORNER, 90)
    assert not maze_card.has_rotated_out_path((-1, 0))
    assert maze_card.has_rotated_out_path((0, 1))
    assert maze_card.has_rotated_out_path((1, 0))
    assert not maze_card.has_rotated_out_path((0, -1))


def test_has_out_path_for_straight_with_rotation_270():
    """ Tests has_rotated_out_path """
    maze_card = MazeCard(0, MazeCard.STRAIGHT, 270)
    assert not maze_card.has_rotated_out_path((-1, 0))
    assert maze_card.has_rotated_out_path((0, 1))
    assert not maze_card.has_rotated_out_path((1, 0))
    assert maze_card.has_rotated_out_path((0, -1))


def test_rotated_out_paths_for_t_junct_with_rotation_180():
    """ Tests out_paths """
    maze_card = MazeCard(0, MazeCard.T_JUNCT, 180)
    assert (-1, 0) in maze_card.rotated_out_paths()
    assert (0, 1) not in maze_card.rotated_out_paths()
    assert (1, 0) in maze_card.rotated_out_paths()
    assert (0, -1) in maze_card.rotated_out_paths()


def test_rotated_out_paths_for_corner_with_rotation_0():
    """ Tests out_paths """
    maze_card = MazeCard(0, MazeCard.CORNER, 0)
    assert (-1, 0) in maze_card.rotated_out_paths()
    assert (0, 1) in maze_card.rotated_out_paths()
    assert (1, 0) not in maze_card.rotated_out_paths()
    assert (0, -1) not in maze_card.rotated_out_paths()
