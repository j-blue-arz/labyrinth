""" Tests for Game of model.py """
import pytest
from domain.model import Game, BoardLocation, MazeCard, Turns
from domain.exceptions import *
from maze_factory import fill_maze


def test_add_find_piece():
    """ Tests add_player and find_piece """
    game = Game()
    player_id1 = game.add_player()
    player_id2 = game.add_player()
    assert game.find_piece(player_id1).identifier == player_id1
    assert game.find_piece(player_id2).identifier == player_id2


def test_accepts_players():
    """ Tests accepts_players """
    game = Game()
    for _ in range(game.MAX_PLAYERS):
        assert game.accepts_players()
        game.add_player()
    assert not game.accepts_players()


def test_init_game_sets_first_player_on_top_left_corner():
    """ Tests init_game """
    game = Game()
    player_ids = [game.add_player() for _ in range(game.MAX_PLAYERS)]
    game.init_game()
    assert game.find_piece(player_ids[0]).maze_card == game.maze[BoardLocation(0, 0)]


def test_init_game_sets_all_players_on_corners():
    """ Tests init_game """
    game = Game()

    def is_corner(location):
        return (location.row in [0, game.maze.MAZE_SIZE - 1]) and (location.column in [0, game.maze.MAZE_SIZE - 1])

    player_ids = [game.add_player() for _ in range(game.MAX_PLAYERS)]
    game.init_game()
    for player_id in player_ids:
        player_location = game.maze.maze_card_location(game.find_piece(player_id).maze_card)
        assert is_corner(player_location)


def test_init_game_gives_all_players_objectives():
    """ Tests init_game """
    game = Game()
    player_ids = [game.add_player() for _ in range(game.MAX_PLAYERS)]
    game.init_game()
    for player_id in player_ids:
        assert game.find_piece(player_id).objective_maze_card


def test_all_player_and_objective_locations_are_different():
    """ Tests init_game. """
    game = Game()
    for _ in range(game.MAX_PLAYERS):
        game.add_player()
    game.init_game()
    _assert_all_player_and_objective_locations_different(game)


def test_objective_locations_after_reaching_location():
    """ Tests new objective generation after reaching one """
    game = Game()
    fill_maze(MAZE_STRING, game.maze)
    game.leftover_card = MazeCard.generate_random()
    player_id = game.add_player()
    player = game.find_piece(player_id)
    player.maze_card = game.maze[BoardLocation(0, 6)]
    player.objective_maze_card = game.maze[BoardLocation(1, 6)]
    game.turns = Turns([player_id], next_action=(player_id, Turns.MOVE_ACTION))
    game.move(player_id, BoardLocation(1, 6))
    _assert_all_player_and_objective_locations_different(game)


def _assert_all_player_and_objective_locations_different(game):
    """ asserts for a given Game instance """
    card_ids = set()
    for player in game.players:
        card_ids.add(player.maze_card.identifier)
        card_ids.add(player.objective_maze_card.identifier)
    assert len(card_ids) == len(game.players) * 2


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
    pushed_out = game.maze[BoardLocation(game.maze.MAZE_SIZE - 1, 1)]
    game.shift(player_id, BoardLocation(0, 1), 270)
    assert pushed_out == game.leftover_card


def test_shift_updates_players_on_pushed_out_card():
    """ Tests shift """
    game = Game()
    player_id = game.add_player()
    player = game.find_piece(player_id)
    game.init_game()
    pushed_card = game.leftover_card
    player.maze_card = game.maze[BoardLocation(0, 3)]
    game.shift(player_id, BoardLocation(game.maze.MAZE_SIZE-1, 3), 90)
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
    with pytest.raises(InvalidShiftLocationException):
        game.shift(player_id, BoardLocation(0, 0), 90)


def test_shift_raises_error_on_invalid_rotation():
    """ Tests shift validation """
    game = Game()
    player_id = game.add_player()
    game.init_game()
    with pytest.raises(InvalidRotationException):
        game.shift(player_id, BoardLocation(0, 1), 70)


def test_shift_raises_error_on_invalid_player_id():
    """ Tests shift validation """
    game = Game()
    player_id = game.add_player()
    game.init_game()
    with pytest.raises(PlayerNotFoundException):
        game.shift(player_id + 1, BoardLocation(0, 1), 90)


def test_move_updates_players_maze_card_correctly():
    """ Tests move
    Instead of calling init_game(), the board is built manually, and
    the player's position is set manually as well, so that
    randomness is eliminated for testing """
    game = Game()
    fill_maze(MAZE_STRING, game.maze)
    game.leftover_card = MazeCard.generate_random()
    player_id = game.add_player()
    game.find_piece(player_id).maze_card = game.maze[BoardLocation(0, 1)]
    game.turns = Turns([player_id], next_action=(player_id, Turns.MOVE_ACTION))
    game.move(player_id, BoardLocation(0, 2))
    assert game.maze[BoardLocation(0, 2)] == game.find_piece(player_id).maze_card


def test_move_raises_error_on_unreachable_location():
    """ Tests move validation """
    game = Game()
    fill_maze(MAZE_STRING, game.maze)
    game.leftover_card = MazeCard.generate_random()
    player_id = game.add_player()
    game.find_piece(player_id).maze_card = game.maze[BoardLocation(0, 1)]
    game.turns = Turns([player_id], next_action=(player_id, Turns.MOVE_ACTION))
    with pytest.raises(MoveUnreachableException):
        game.move(player_id, BoardLocation(0, 0))


def test_move_raises_error_on_invalid_location():
    """ Tests move validation """
    game = Game()
    player_id = game.add_player()
    game.init_game()
    game.turns.perform_action(player_id, Turns.SHIFT_ACTION)
    with pytest.raises(InvalidLocationException):
        game.move(player_id, BoardLocation(-1, -1))


def test_move_raises_error_on_invalid_player_id():
    """ Tests move validation """
    game = Game()
    player_id = game.add_player()
    game.init_game()
    with pytest.raises(PlayerNotFoundException):
        game.move(player_id - 1, BoardLocation(5, 5))


MAZE_STRING = """
###|#.#|#.#|###|#.#|#.#|###|
#..|#..|...|...|#..|..#|..#|
#.#|###|###|#.#|###|###|#.#|
---------------------------|
###|###|#.#|#.#|#.#|#.#|#.#|
...|...|#.#|#..|#.#|...|..#|
#.#|#.#|#.#|###|#.#|###|#.#|
---------------------------|
#.#|#.#|#.#|#.#|#.#|#.#|#.#|
#..|#..|..#|#..|..#|#.#|..#|
#.#|#.#|#.#|#.#|#.#|#.#|#.#|
---------------------------|
#.#|#.#|#.#|###|#.#|###|###|
..#|..#|#..|...|...|...|..#|
###|#.#|###|#.#|###|#.#|#.#|
---------------------------|
###|#.#|###|#.#|###|#.#|###|
#..|..#|#..|#.#|...|#..|...|
#.#|###|#.#|#.#|#.#|###|###|
---------------------------|
###|#.#|###|#.#|#.#|#.#|#.#|
..#|#..|...|...|#.#|#..|..#|
#.#|#.#|###|###|#.#|#.#|#.#|
---------------------------|
#.#|#.#|###|###|#.#|#.#|#.#|
#..|...|...|...|#.#|...|..#|
###|###|#.#|###|#.#|###|###|
---------------------------*

"""
