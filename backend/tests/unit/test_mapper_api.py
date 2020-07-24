""" This module tests mapper module.
More specifically, it tests the method game_state_to_dto(),
which maps a Game instance to an object used to transfer the state """
import json
import app.mapper.api as mapper
import app.mapper.constants as keys
from app.model.game import BoardLocation, Player
from app.model.factories import create_game
from app.model.computer import ComputerPlayer


def _create_test_game():
    """ Creates a Game instance,
    returns this instance and one of the player's identifier """
    game = create_game(game_id=3)
    game.previous_shift_location = BoardLocation(0, 1)
    player_id = game.add_player(Player)
    game.add_player(Player)
    game.add_player(ComputerPlayer, algorithm_name="random", shift_url="shift-url",
                    move_url="move-url")
    game.get_player(player_id).score = 9
    game.start_game()
    return game


def test_mapping_players():
    """ Tests correct mapping of players """
    game = _create_test_game()
    game_dto = mapper.game_state_to_dto(game)
    assert keys.PLAYERS in game_dto
    assert len(game_dto[keys.PLAYERS]) == len(game.board.pieces)
    assert len(game_dto[keys.PLAYERS]) == len(game.players)
    for player_dto in game_dto[keys.PLAYERS]:
        assert keys.ID in player_dto
        player_game = game.get_player(player_dto[keys.ID])
        assert player_game
        assert player_dto[keys.MAZE_CARD_ID] == player_game.piece.maze_card.identifier
        assert keys.OBJECTIVE not in player_dto
        assert keys.SCORE in player_dto
        assert player_dto[keys.SCORE] == player_game.score
        assert player_dto[keys.PIECE_INDEX] == player_game.piece.piece_index


def test_mapping_computer_player():
    """ Tests correct mapping of information about computer player """
    game = _create_test_game()
    game_dto = mapper.game_state_to_dto(game)
    computer_player_dto = game_dto[keys.PLAYERS][2]
    assert computer_player_dto[keys.IS_COMPUTER]
    assert computer_player_dto[keys.ALGORITHM] == "random"
    player_dto = game_dto[keys.PLAYERS][1]
    assert not player_dto[keys.IS_COMPUTER]
    assert keys.ALGORITHM not in player_dto


def test_mapping_leftover():
    """ Tests correct mapping of leftover maze card """
    game = _create_test_game()
    game_dto = mapper.game_state_to_dto(game)
    maze_cards = game_dto[keys.MAZE][keys.MAZE_CARDS]
    leftover_dtos = [maze_card for maze_card in maze_cards
                     if not maze_card[keys.LOCATION]]
    assert len(leftover_dtos) == 1
    leftover_dto = leftover_dtos[0]
    assert leftover_dto[keys.ID] == game.board.leftover_card.identifier
    assert leftover_dto[keys.OUT_PATHS] == game.board.leftover_card.out_paths


def test_mapping_board():
    """ Tests correct mapping of current board state """
    game = _create_test_game()
    game_dto = mapper.game_state_to_dto(game)
    maze_cards = game_dto[keys.MAZE][keys.MAZE_CARDS]
    maze_card_dtos = [maze_card_dto for maze_card_dto in maze_cards
                      if maze_card_dto[keys.LOCATION]]
    assert game_dto[keys.MAZE][keys.MAZE_SIZE] == game.board.maze.maze_size
    assert len(maze_card_dtos) == game.board.maze.maze_size * game.board.maze.maze_size
    ids = set()
    for maze_card_dto in maze_card_dtos:
        location = _assert_and_return_location_dto(maze_card_dto[keys.LOCATION])
        maze_card_game = game.board.maze[location]
        assert maze_card_dto[keys.ID] == maze_card_game.identifier
        assert maze_card_dto[keys.OUT_PATHS] == maze_card_game.out_paths
        assert maze_card_dto[keys.ROTATION] == maze_card_game.rotation
        ids.add(maze_card_dto[keys.ID])
    assert len(ids) == len(maze_card_dtos)


def test_mapping_objectives():
    """ Tests correct mapping of players' objective """
    game = _create_test_game()
    game_dto = mapper.game_state_to_dto(game)
    assert keys.OBJECTIVE in game_dto
    assert game_dto[keys.OBJECTIVE] == game.board.objective_maze_card.identifier


def test_mapping_enabled_shift_loctions():
    """ Tests correct mapping of enabled shift loctions """
    game = _create_test_game()
    game_dto = mapper.game_state_to_dto(game)
    assert keys.ENABLED_SHIFT_LOCATIONS in game_dto
    assert len(game_dto[keys.ENABLED_SHIFT_LOCATIONS]) == 11
    for enabled_shift_location in game_dto[keys.ENABLED_SHIFT_LOCATIONS]:
        assert keys.ROW in enabled_shift_location
        assert keys.COLUMN in enabled_shift_location


def test_mapping_identifier():
    """ Tests correct mapping of game's identifier """
    game = _create_test_game()
    game_dto = mapper.game_state_to_dto(game)
    assert game_dto[keys.ID] == game.identifier


def test_dto_to_shift_action():
    """ Tests dto_to_shift_action """
    shift_dto = json.loads("""{"location": {"row": 3,"column": 4},"leftoverRotation": 5}""")
    location, rotation = mapper.dto_to_shift_action(shift_dto)
    assert location.row == 3
    assert location.column == 4
    assert rotation == 5


def test_dto_to_move_action():
    """ Tests dto_to_move_action """
    move_dto = json.loads("""{"location": {"row": 5,"column": 1}}""")
    location = mapper.dto_to_move_action(move_dto)
    assert location.row == 5
    assert location.column == 1


def test_dto_to_type():
    """ Tests dto_to_type """
    player_request_dto = json.loads("""{"type": "normal"}""")
    player_type = mapper.dto_to_type(player_request_dto)
    assert player_type == "normal"


def test_dto_to_type_with_none():
    """ Tests dto_to_type """
    player_request_dto = None
    player_type = mapper.dto_to_type(player_request_dto)
    assert player_type is None


def test_shift_action_to_dto():
    """ Tests shift_action_to_dto """
    shift_dto = mapper.shift_action_to_dto(BoardLocation(1, 2), 180)
    assert keys.LOCATION in shift_dto
    location = _assert_and_return_location_dto(shift_dto[keys.LOCATION])
    assert location.row == 1
    assert location.column == 2
    assert keys.LEFTOVER_ROTATION in shift_dto
    assert shift_dto[keys.LEFTOVER_ROTATION] == 180


def test_move_action_to_dto():
    """ Tests move_action_to_dto """
    move_dto = mapper.move_action_to_dto(BoardLocation(3, 4))
    assert keys.LOCATION in move_dto
    location = _assert_and_return_location_dto(move_dto[keys.LOCATION])
    assert location.row == 3
    assert location.column == 4


def test_dto_to_maze_size():
    """ Tests dto_to_maze_size """
    game_options_dto = json.loads("""{"mazeSize": 9}""")
    size = mapper.dto_to_maze_size(game_options_dto)
    assert size == 9


def _assert_and_return_location_dto(location_dto):
    assert location_dto
    assert keys.ROW in location_dto
    assert keys.COLUMN in location_dto
    return BoardLocation(location_dto[keys.ROW], location_dto[keys.COLUMN])
