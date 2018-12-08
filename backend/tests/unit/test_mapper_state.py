""" This module tests mapper module.
More specifically, it tests the method player_state_to_dto(), 
which maps a Game instance to an object used to transfer the state,
as seen from one player. """
import server.mapper as mapper
from domain.model import Game, BoardLocation


def _create_test_game():
    """ Creates a Game instance,
    returns this instance and one of the player's identifier """
    game = Game()
    player_ids = [game.add_player(), game.add_player(), game.add_player()]
    game.init_game()
    return game, player_ids[1]


def test_mapping_players():
    """ Tests correct mapping of players """
    game, player_id = _create_test_game()
    game_dto = mapper.player_state_to_dto(game, player_id)
    assert mapper.PLAYERS in game_dto
    assert len(game_dto[mapper.PLAYERS]) == len(game.board.pieces)
    assert len(game_dto[mapper.PLAYERS]) == len(game._player_ids)
    for player_dto in game_dto[mapper.PLAYERS]:
        assert mapper.ID in player_dto
        player_game = game.board.find_piece(player_dto[mapper.ID])
        assert player_game
        assert player_dto[mapper.MAZE_CARD_ID] == player_game.maze_card.identifier
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
    assert game_dto[mapper.OBJECTIVE] == game.board.find_piece(player_id).objective_maze_card.identifier


def _assert_and_return_location_dto(location_dto):
    assert location_dto
    assert mapper.ROW in location_dto
    assert mapper.COLUMN in location_dto
    return BoardLocation(location_dto[mapper.ROW], location_dto[mapper.COLUMN])
