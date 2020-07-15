""" Tests for BoardLocation of game.py """
from app.model.game import BoardLocation


def test_add_should_not_alter_current():
    """ Tests add method of BoardLocation """
    location = BoardLocation(0, 0)
    location.add(1, 0)
    assert location.row == 0
    assert location.column == 0


def test_add_should_return_correct_location():
    """ Tests add method of BoardLocation """
    location = BoardLocation(0, 0)
    new_location = location.add(1, 0)
    assert new_location.row == 1
    assert new_location.column == 0
