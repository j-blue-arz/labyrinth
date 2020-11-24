""" Tests for Game of game.py """
from unittest.mock import Mock, call, PropertyMock
import pytest
from labyrinth.model.game import Game, BoardLocation, Player, PlayerAction, Board, Turns
from labyrinth.model import factories
from labyrinth.model.exceptions import PlayerNotFoundException, GameFullException


def test_add_get_player():
    """ Tests add_player and get_player """
    game = Game(identifier=0)
    player = Player(7)
    game.add_player(player)
    assert game.get_player(7) is player


def test_get_player_raises_exception_for_unknown_id():
    """ Tests get_player """
    game = Game(identifier=0)
    with pytest.raises(PlayerNotFoundException):
        game.get_player(0)


def test_add_player_with_duplicate_id_does_not_add():
    """ Tests add_player """
    game = Game(identifier=0)
    game.add_player(Player(1))
    game.add_player(Player(1))
    assert len(game.players) == 1


def test_unused_player_id_returns_new_id():
    """ Tests unused_player_id """
    game = Game(identifier=0)
    game.add_player(Player(3))
    game.add_player(Player(7))
    game.add_player(Player(11))
    player_id = game.unused_player_id()
    assert player_id not in [player.identifier for player in game.players]


def test_unused_player_id_raises_exception_on_full_game():
    """ Tests unused_player_id """
    game = Game(identifier=0)
    for _ in range(game.MAX_PLAYERS):
        player_id = game.unused_player_id()
        game.add_player(Player(player_id))
    with pytest.raises(GameFullException):
        player_id = game.unused_player_id()


def given_empty_game__when_adding_players__creates_pieces_on_board():
    board = Board()
    game = Game(identifier=0, board=board, turns=Mock())
    for _ in range(4):
        player_id = game.unused_player_id()
        game.add_player(Player(player_id))
    assert len(board.pieces) == 4


def test_given_empty_game__when_player_is_added__initializes_turns():
    game = Game(identifier=0)

    player = Player(game.unused_player_id())
    game.add_player(player)

    game.turns.next_player_action() == PlayerAction(player, PlayerAction.PREPARE)


def test_add_player_validation():
    """ Tests that adding more players than MAX_PLAYERS does not add another one """
    game = Game(identifier=0)
    for _ in range(game.MAX_PLAYERS):
        player_id = game.unused_player_id()
        game.add_player(Player(player_id))
    with pytest.raises(GameFullException):
        game.add_player(Player(42))


def test_shift_raises_error_on_invalid_player_id():
    """ Tests shift validation """
    game = Game(identifier=0, turns=Turns())
    player_id = game.unused_player_id()
    game.add_player(Player(player_id))
    with pytest.raises(PlayerNotFoundException):
        game.shift(player_id + 1, BoardLocation(0, 1), 90)


def test_move_raises_error_on_invalid_player_id():
    """ Tests move validation """
    game = Game(identifier=0, turns=Turns())
    player_id = game.unused_player_id()
    game.add_player(Player(player_id))
    with pytest.raises(PlayerNotFoundException):
        game.move(player_id - 1, BoardLocation(5, 5))


def test_move_raises_error_on_invalid_turn():
    """ Tests turn validation """
    board = Mock()
    turns = Mock()
    turns.is_action_possible.return_value = False
    game = Game(identifier=0, board=board, turns=turns)
    player_id = game.unused_player_id()
    game.add_player(Player(player_id))
    player = game.get_player(player_id)
    game.move(player_id, BoardLocation(0, 0))
    board.move.assert_not_called()
    turns.is_action_possible.assert_called_once_with(player, PlayerAction.MOVE_ACTION)


def test_move_does_not_raise_error_after_shift():
    """ Tests turn validation """
    board = Mock()
    turns = Mock()
    turns.is_action_possible.return_value = True
    game = Game(identifier=0, board=board, turns=turns)
    player_id = game.unused_player_id()
    game.add_player(Player(player_id))
    player = game.get_player(player_id)
    game.move(player_id, BoardLocation(0, 0))
    board.move.assert_called_once()
    turns.is_action_possible.assert_called_once_with(player, PlayerAction.MOVE_ACTION)


def test_get_enabled_shift_locations_without_previous_shift():
    """ Tests get_enabled_shift_locations where the previous shift is None """
    board = Board()
    game = Game(identifier=0, board=board)
    enabled_shift_locations = game.get_enabled_shift_locations()
    assert set(enabled_shift_locations) == set(board.shift_locations)


def test_get_enabled_shift_locations_with_previous_shift():
    """ Tests get_enabled_shift_locations where the previous shift is (3, 0) """
    board = Board()
    game = Game(identifier=0, board=board)
    game.previous_shift_location = BoardLocation(3, 0)
    expected_disabled = BoardLocation(3, board.maze.maze_size - 1)
    enabled_shift_locations = game.get_enabled_shift_locations()
    assert expected_disabled not in enabled_shift_locations


def test_player_reaches_objective_increase_score():
    """ Tests that the score on a player is increased once he reaches an objective """
    board = Mock()
    turns = Mock()
    turns.is_action_possible.return_value = True
    board.move.return_value = True
    game = Game(identifier=0, board=board, turns=turns)
    player_id = game.unused_player_id()
    game.add_player(Player(player_id))
    old_score = game.get_player(player_id).score
    game.move(player_id, BoardLocation(0, 1))
    assert game.get_player(player_id).score == old_score + 1


def test_replace_board():
    """ Tests replace_board. Asserts that score and all player locations are reset,
    and that it is the first player's turn
    """
    turns = Mock()
    game = Game(identifier=0, turns=turns)
    player_ids = []
    for _ in range(2):
        player_id = game.unused_player_id()
        game.add_player(Player(player_id))
        player_ids.append(player_id)
    players = list(map(game.get_player, player_ids))
    players[0].score = 11
    players[1].score = 22
    players[0].piece.maze_card = game.board.maze[BoardLocation(1, 1)]
    players[1].piece.maze_card = game.board.maze[BoardLocation(2, 2)]
    pieces = list(map(lambda player: player.piece, players))

    board = Mock()
    type(board).pieces = PropertyMock(return_value=pieces)
    turns.reset_mock()
    game.replace_board(board)

    board.create_piece.assert_has_calls([call(), call()])
    turns.start.assert_called_once()
    assert players[0].score == 0
    assert players[1].score == 0


def _turn_listener_test_setup(players):
    game = factories.create_game(game_id=7, with_delay=False)
    listener = Mock()
    game.register_turn_change_listener(listener)
    for player in players:
        game.add_player(player)
    return game, listener


def given_empty_game__when_first_player_is_added__turn_listener_is_notified():
    player = Player(0)
    game, listener = _turn_listener_test_setup([])

    listener.reset_mock()
    game.add_player(player)
    listener.assert_called_once_with(game=game, player=player, next_action=PlayerAction.SHIFT_ACTION)


def test_register_turn_listener__when_current_player_is_deleted__listener_is_notified():
    players = [Player(0), Player(1)]
    game, listener = _turn_listener_test_setup(players)

    listener.reset_mock()
    game.remove_player(players[0].identifier)
    listener.assert_called_once_with(game=game, player=players[1], next_action=PlayerAction.SHIFT_ACTION)


def test_register_turn_listener__when_first_player_is_added__listener_is_notified():
    game, listener = _turn_listener_test_setup([Player(0)])
    game.remove_player(0)
    player = Player(1)

    listener.reset_mock()
    game.add_player(player)
    listener.assert_called_once_with(game=game, player=player, next_action=PlayerAction.SHIFT_ACTION)


def test_register_turn_listener__when_player_shifts__listener_is_notified():
    player = Player(0)
    game, listener = _turn_listener_test_setup([player])

    listener.reset_mock()
    game.shift(0, BoardLocation(0, 1), 0)
    listener.assert_called_once_with(game=game, player=player, next_action=PlayerAction.MOVE_ACTION)


def test_register_turn_listener__when_player_moves__listener_is_notified():
    players = [Player(0), Player(1)]
    game, listener = _turn_listener_test_setup(players)
    game.shift(0, BoardLocation(0, 1), 0)

    listener.reset_mock()
    game.move(0, BoardLocation(0, 0))
    listener.assert_called_once_with(game=game, player=players[1], next_action=PlayerAction.SHIFT_ACTION)
