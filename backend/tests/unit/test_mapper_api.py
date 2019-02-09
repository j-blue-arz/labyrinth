""" This module tests mapper module.
More specifically, it tests the method game_state_to_dto(),
which maps a Game instance to an object used to transfer the state """
import json
import server.mapper.api as mapper
from server.model.game import BoardLocation, Player
from server.model.factories import create_game
from server.model.computer import ComputerPlayer


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
    assert mapper.PLAYERS in game_dto
    assert len(game_dto[mapper.PLAYERS]) == len(game.board.pieces)
    assert len(game_dto[mapper.PLAYERS]) == len(game.players)
    for player_dto in game_dto[mapper.PLAYERS]:
        assert mapper.ID in player_dto
        player_game = game.get_player(player_dto[mapper.ID])
        assert player_game
        assert player_dto[mapper.MAZE_CARD_ID] == player_game.piece.maze_card.identifier
        assert mapper.OBJECTIVE not in player_dto
        assert mapper.SCORE in player_dto
        assert player_dto[mapper.SCORE] == player_game.score
        assert player_dto[mapper.PIECE_INDEX] == player_game.piece.piece_index


def test_mapping_computer_player():
    """ Tests correct mapping of information about computer player """
    game = _create_test_game()
    game_dto = mapper.game_state_to_dto(game)
    computer_player_dto = game_dto[mapper.PLAYERS][2]
    assert computer_player_dto[mapper.IS_COMPUTER]
    assert computer_player_dto[mapper.ALGORITHM] == "random"
    player_dto = game_dto[mapper.PLAYERS][1]
    assert not player_dto[mapper.IS_COMPUTER]
    assert mapper.ALGORITHM not in player_dto


def test_mapping_leftover():
    """ Tests correct mapping of leftover maze card """
    game = _create_test_game()
    game_dto = mapper.game_state_to_dto(game)
    maze_cards = game_dto[mapper.MAZE][mapper.MAZE_CARDS]
    leftover_dtos = [maze_card for maze_card in maze_cards
                     if not maze_card[mapper.LOCATION]]
    assert len(leftover_dtos) == 1
    leftover_dto = leftover_dtos[0]
    assert leftover_dto[mapper.ID] == game.board.leftover_card.identifier
    assert leftover_dto[mapper.DOORS] == game.board.leftover_card.doors


def test_mapping_board():
    """ Tests correct mapping of current board state """
    game = _create_test_game()
    game_dto = mapper.game_state_to_dto(game)
    maze_cards = game_dto[mapper.MAZE][mapper.MAZE_CARDS]
    maze_card_dtos = [maze_card_dto for maze_card_dto in maze_cards
                      if maze_card_dto[mapper.LOCATION]]
    assert game_dto[mapper.MAZE][mapper.MAZE_SIZE] == game.board.maze.maze_size
    assert len(maze_card_dtos) == game.board.maze.maze_size * game.board.maze.maze_size
    ids = set()
    for maze_card_dto in maze_card_dtos:
        location = _assert_and_return_location_dto(maze_card_dto[mapper.LOCATION])
        maze_card_game = game.board.maze[location]
        assert maze_card_dto[mapper.ID] == maze_card_game.identifier
        assert maze_card_dto[mapper.DOORS] == maze_card_game.doors
        assert maze_card_dto[mapper.ROTATION] == maze_card_game.rotation
        ids.add(maze_card_dto[mapper.ID])
    assert len(ids) == len(maze_card_dtos)


def test_mapping_objectives():
    """ Tests correct mapping of players' objective """
    game = _create_test_game()
    game_dto = mapper.game_state_to_dto(game)
    assert mapper.OBJECTIVE in game_dto
    assert game_dto[mapper.OBJECTIVE] == game.board.objective_maze_card.identifier


def test_mapping_enabled_shift_loctions():
    """ Tests correct mapping of enabled shift loctions """
    game = _create_test_game()
    game_dto = mapper.game_state_to_dto(game)
    assert mapper.ENABLED_SHIFT_LOCATIONS in game_dto
    assert len(game_dto[mapper.ENABLED_SHIFT_LOCATIONS]) == 11
    for enabled_shift_location in game_dto[mapper.ENABLED_SHIFT_LOCATIONS]:
        assert mapper.ROW in enabled_shift_location
        assert mapper.COLUMN in enabled_shift_location

def test_mapping_identifier():
    """ Tests correct mapping of game's identifier """
    game = _create_test_game()
    game_dto = mapper.game_state_to_dto(game)
    assert game_dto[mapper.ID] == game.identifier


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


def test_dto_to_type_and_alone_with_none():
    """ Tests dto_to_type """
    player_request_dto = None
    player_type = mapper.dto_to_type(player_request_dto)
    assert player_type is None


def test_shift_action_to_dto():
    """ Tests shift_action_to_dto """
    shift_dto = mapper.shift_action_to_dto(BoardLocation(1, 2), 180)
    assert mapper.LOCATION in shift_dto
    location = _assert_and_return_location_dto(shift_dto[mapper.LOCATION])
    assert location.row == 1
    assert location.column == 2
    assert mapper.LEFTOVER_ROTATION in shift_dto
    assert shift_dto[mapper.LEFTOVER_ROTATION] == 180


def test_move_action_to_dto():
    """ Tests move_action_to_dto """
    move_dto = mapper.move_action_to_dto(BoardLocation(3, 4))
    assert mapper.LOCATION in move_dto
    location = _assert_and_return_location_dto(move_dto[mapper.LOCATION])
    assert location.row == 3
    assert location.column == 4

def test_dto_to_maze_size():
    """ Tests dto_to_maze_size """
    game_options_dto = json.loads("""{"mazeSize": 9}""")
    size = mapper.dto_to_maze_size(game_options_dto)
    assert size == 9


def _assert_and_return_location_dto(location_dto):
    assert location_dto
    assert mapper.ROW in location_dto
    assert mapper.COLUMN in location_dto
    return BoardLocation(location_dto[mapper.ROW], location_dto[mapper.COLUMN])
