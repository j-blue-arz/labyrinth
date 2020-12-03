""" Tests for Game of game.py """
from unittest.mock import Mock
import pytest
from labyrinth.model.game import Game, BoardLocation, Player, PlayerAction, Board, Turns
import labyrinth.model.factories as factory
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
    add_players(game, game.MAX_PLAYERS)
    with pytest.raises(GameFullException):
        _ = game.unused_player_id()


def given_empty_game__when_adding_players__creates_pieces_on_board():
    board = Board()
    game = Game(identifier=0, board=board, turns=Mock())
    add_players(game, 4)
    assert len(board.pieces) == 4


def test_given_empty_game__when_player_is_added__initializes_turns():
    game = Game(identifier=0)

    player = Player(game.unused_player_id())
    game.add_player(player)

    game.turns.next_player_action() == PlayerAction(player, PlayerAction.PREPARE_SHIFT)


def test_add_player_validation():
    """ Tests that adding more players than MAX_PLAYERS does not add another one """
    game = Game(identifier=0)
    add_players(game, game.MAX_PLAYERS)
    with pytest.raises(GameFullException):
        game.add_player(Player(42))


def test_shift_raises_error_on_invalid_player_id():
    """ Tests shift validation """
    game = Game(identifier=0, turns=Turns())
    player_id = add_player(game)
    with pytest.raises(PlayerNotFoundException):
        game.shift(player_id + 1, BoardLocation(0, 1), 90)


def test_move_raises_error_on_invalid_player_id():
    """ Tests move validation """
    game = Game(identifier=0, turns=Turns())
    player_id = add_player(game)
    with pytest.raises(PlayerNotFoundException):
        game.move(player_id - 1, BoardLocation(5, 5))


def test_move_raises_error_on_invalid_turn():
    """ Tests turn validation """
    board = Mock()
    turns = Mock()
    turns.is_action_possible.return_value = False
    game = Game(identifier=0, board=board, turns=turns)
    player_id = add_player(game)
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
    player_id = add_player(game)
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
    player_id = add_player(game)
    old_score = game.get_player(player_id).score
    game.move(player_id, BoardLocation(0, 1))
    assert game.get_player(player_id).score == old_score + 1


def given_game_with_two_players__when_restart__then_players_keep_piece_index():
    game = Game(identifier=0)
    add_players(game, 2)
    old_player_pieces = {player.id: player.piece for player in game.players}

    restart(game)

    for player in game.players:
        expected_piece_index = old_player_pieces[player.id].piece_index
        assert player.piece.piece_index == expected_piece_index


def given_game_with_two_players__when_restart__then_score_is_reset():
    game = Game(identifier=0)
    add_players(game, 2)
    game.players[0].score = 11
    game.players[1].score = 22

    restart(game)

    assert game.players[0].score == 0
    assert game.players[1].score == 0


def given_running_game__when_restart__then_turns_are_started():
    turns = Mock()
    game = Game(identifier=0, turns=turns)
    game.add_player(Player(0))
    turns.reset_mock()

    restart(game)

    turns.start.assert_called_once()


def given_game_player_with_piece_index_0_removed__when_restart__then_remaining_player_keeps_piece_index():
    game = Game(identifier=0)
    add_players(game, 2)
    remove_player_with_piece_index(game, 0)
    remaining_piece = game.players[0].piece

    restart(game)

    assert game.players[0].piece.piece_index == remaining_piece.piece_index


def given_game_player_with_piece_index_0_removed__when_restart__then_remaining_player_has_same_start_location():
    game = Game(identifier=0)
    add_players(game, 2)
    remove_player_with_piece_index(game, 0)
    old_player_start_location = get_player_piece_location(game, game.players[0])
    set_player_piece_location(game, game.players[0], BoardLocation(4, 4))

    restart(game)

    assert get_player_piece_location(game, game.players[0]) == old_player_start_location


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
    listener.assert_called_once_with(game=game, next_player_action=PlayerAction(player, PlayerAction.SHIFT_ACTION))


def test_register_turn_listener__when_current_player_is_deleted__listener_is_notified():
    players = [Player(0), Player(1)]
    game, listener = _turn_listener_test_setup(players)

    listener.reset_mock()
    game.remove_player(players[0].identifier)
    listener.assert_called_once_with(game=game, next_player_action=PlayerAction(players[1], PlayerAction.SHIFT_ACTION))


def test_register_turn_listener__when_first_player_is_added__listener_is_notified():
    game, listener = _turn_listener_test_setup([Player(0)])
    game.remove_player(0)
    player = Player(1)

    listener.reset_mock()
    game.add_player(player)
    listener.assert_called_once_with(game=game, next_player_action=PlayerAction(player, PlayerAction.SHIFT_ACTION))


def test_register_turn_listener__when_player_shifts__listener_is_notified():
    player = Player(0)
    game, listener = _turn_listener_test_setup([player])

    listener.reset_mock()
    game.shift(0, BoardLocation(0, 1), 0)
    listener.assert_called_once_with(game=game, next_player_action=PlayerAction(player, PlayerAction.MOVE_ACTION))


def test_register_turn_listener__when_player_moves__listener_is_notified():
    players = [Player(0), Player(1)]
    game, listener = _turn_listener_test_setup(players)
    game.shift(0, BoardLocation(0, 1), 0)

    listener.reset_mock()
    game.move(0, BoardLocation(0, 0))
    listener.assert_called_once_with(game=game, next_player_action=PlayerAction(players[1], PlayerAction.SHIFT_ACTION))


def add_players(game, number_of_players):
    for _ in range(number_of_players):
        add_player(game)


def add_player(game):
    """ Adds a player, using the next unused player id """
    player_id = game.unused_player_id()
    game.add_player(Player(player_id))
    return player_id


def restart(game):
    board = factory.create_board(maze_size=9)
    game.restart(board)


def remove_player_with_piece_index(game, index):
    player_to_remove = [player for player in game.players if player.piece.piece_index == 0][index]
    game.remove_player(player_to_remove.id)


def get_player_piece_location(game, player):
    return game.board.maze.maze_card_location(player.piece.maze_card)


def set_player_piece_location(game, player, location):
    player.piece.maze_card = game.board.maze[location]
