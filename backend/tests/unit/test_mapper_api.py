""" This module tests mapper module.
More specifically, it tests the method player_state_to_dto(),
which maps a Game instance to an object used to transfer the state,
as seen from one player. """
import json
import mapper.api as mapper
from mapper import constants
from domain.model import BoardLocation, Player
from domain.factories import create_game


def _create_test_game():
    """ Creates a Game instance,
    returns this instance and one of the player's identifier """
    game = create_game()
    player_ids = [game.add_player(Player), game.add_player(Player),
                  game.add_player(Player)]
    game.start_game()
    return game, player_ids[1]


def test_mapping_players():
    """ Tests correct mapping of players """
    game, player_id = _create_test_game()
    game_dto = mapper.player_state_to_dto(game, player_id)
    assert mapper.PLAYERS in game_dto
    assert len(game_dto[mapper.PLAYERS]) == len(game.board.pieces)
    assert len(game_dto[mapper.PLAYERS]) == len(game.players)
    for player_dto in game_dto[mapper.PLAYERS]:
        assert mapper.ID in player_dto
        player_game = game.get_player(player_dto[mapper.ID])
        assert player_game
        assert player_dto[mapper.MAZE_CARD_ID] == player_game.piece.maze_card.identifier
        assert mapper.OBJECTIVE not in player_dto


def test_mapping_leftover():
    """ Tests correct mapping of leftover maze card """
    game, player_id = _create_test_game()
    game_dto = mapper.player_state_to_dto(game, player_id)
    assert mapper.MAZE_CARDS in game_dto
    leftover_dtos = [maze_card_dto for maze_card_dto in game_dto[mapper.MAZE_CARDS]
                     if not maze_card_dto[mapper.LOCATION]]
    assert len(leftover_dtos) == 1
    leftover_dto = leftover_dtos[0]
    assert leftover_dto[mapper.ID] == game.board.leftover_card.identifier
    assert leftover_dto[mapper.DOORS] == game.board.leftover_card.doors


def test_mapping_board():
    """ Tests correct mapping of current board state """
    game, player_id = _create_test_game()
    game_dto = mapper.player_state_to_dto(game, player_id)
    assert mapper.MAZE_CARDS in game_dto
    maze_card_dtos = [maze_card_dto for maze_card_dto in game_dto[mapper.MAZE_CARDS]
                      if maze_card_dto[mapper.LOCATION]]
    assert len(maze_card_dtos) == game.board.maze.MAZE_SIZE * game.board.maze.MAZE_SIZE
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
    game, player_id = _create_test_game()
    game_dto = mapper.player_state_to_dto(game, player_id)
    assert mapper.OBJECTIVE in game_dto
    assert game_dto[mapper.OBJECTIVE] == game.get_player(player_id).piece.objective_maze_card.identifier


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
    """ Tests dto_to_type_and_alone_flag """
    add_player_dto = json.loads("""{"type": "normal"}""")
    player_type, alone = mapper.dto_to_type_and_alone_flag(add_player_dto)
    assert player_type == "normal"
    assert alone is None


def test_dto_to_type_and_alone_with_none():
    """ Tests dto_to_type_and_alone_flag """
    add_player_dto = None
    player_type, alone = mapper.dto_to_type_and_alone_flag(add_player_dto)
    assert player_type is None
    assert alone is None

def test_dto_to_alone_true():
    """ Tests dto_to_type_and_alone_flag """
    add_player_dto = json.loads("""{"alone": true}""")
    player_type, alone = mapper.dto_to_type_and_alone_flag(add_player_dto)
    assert player_type is None
    assert alone is True

def test_dto_to_alone_false():
    """ Tests dto_to_type_and_alone_flag """
    add_player_dto = json.loads("""{"alone": false}""")
    player_type, alone = mapper.dto_to_type_and_alone_flag(add_player_dto)
    assert player_type is None
    assert alone is False

def test_shift_action_to_dto():
    """ Tests shift_action_to_dto """
    shift_dto = mapper.shift_action_to_dto(BoardLocation(1, 2), 180)
    assert constants.LOCATION in shift_dto
    location = _assert_and_return_location_dto(shift_dto[constants.LOCATION])
    assert location.row == 1
    assert location.column == 2
    assert constants.LEFTOVER_ROTATION in shift_dto
    assert shift_dto[constants.LEFTOVER_ROTATION] == 180


def test_move_action_to_dto():
    """ Tests move_action_to_dto """
    move_dto = mapper.move_action_to_dto(BoardLocation(3, 4))
    assert constants.LOCATION in move_dto
    location = _assert_and_return_location_dto(move_dto[constants.LOCATION])
    assert location.row == 3
    assert location.column == 4


def _assert_and_return_location_dto(location_dto):
    assert location_dto
    assert mapper.ROW in location_dto
    assert mapper.COLUMN in location_dto
    return BoardLocation(location_dto[mapper.ROW], location_dto[mapper.COLUMN])
