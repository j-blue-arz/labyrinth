""" Mapper implementation, maps between Model objects and Data Transfer Objects (DTOs).

There are no specific classes for these DTOs,
instead they are data structures built of dictionaries and lists,
which in turn are automatically translatable to structured text (JSON or XML)
"""
from server.model.game import Game, Turns, Player
from .shared import _objective_to_dto, _maze_cards_to_dto, _dto_to_board_location, _board_location_to_dto
from .constants import *


def player_state_to_dto(game: Game, player_id):
    """Maps a game, as seen from one player, to a DTO.

    :param game: an instance of model.Game
    :param player_id: the identifier of the player.
    :return: a structure whose JSON representation is valid for the API
    """
    game_dto = dict()
    player = next(player for player in game.players if player.identifier == player_id)
    game_dto[OBJECTIVE] = _objective_to_dto(game.board.objective_maze_card)
    game_dto[PLAYERS] = [_player_to_dto(player) for player in game.players]
    game_dto[MAZE_CARDS] = _maze_cards_to_dto(game.board)
    game_dto[NEXT_ACTION] = _turns_to_next_player_action_dto(game.turns)
    return game_dto


def dto_to_shift_action(shift_dto):
    """ Maps the DTO for the shift api method to the parameters of the model method
    :param shift_dto: a dictionary representing the body of the shift api method.
    Expected to be of the form
    {
        location: {
            row: <int>
            column: <int>
        },
        leftoverRotation: <int>
    }
    :return: a BoardLocation instance and an integer for the leftover maze card rotation
    """
    return _dto_to_board_location(shift_dto[LOCATION]), shift_dto[LEFTOVER_ROTATION]


def dto_to_move_action(move_dto):
    """ Maps the DTO for the move api method to the parameters of the model method
    :param move_dto: a dictionary representing the body of the move api method.
    Expected to be of the form
    {
        location: {
            row: <int>
            column: <int>
        }
    }
    :return: a BoardLocation instance
    """
    return _dto_to_board_location(move_dto[LOCATION])


def dto_to_type_and_alone_flag(add_player_dto):
    """ Maps a DTO for the add player api method to two values, the type and the flag 'alone' """
    if isinstance(add_player_dto, dict):
        return _value_or_none(add_player_dto, POST_PLAYER_TYPE), _value_or_none(add_player_dto, POST_PLAYER_ALONE)
    return None, None


def _value_or_none(dto, key):
    if key in dto:
        return dto[key]
    return None


def shift_action_to_dto(insert_location, insert_rotation):
    """ Maps an insert location and the rotation of the leftover maze card to a DTO, which is valid
    for the POST shift method of the API """
    return {"location":  _board_location_to_dto(insert_location),
            "leftoverRotation": insert_rotation}


def move_action_to_dto(move_location):
    """ Maps a location to a DTO, which is valid for the POST move method of the API """
    return {"location":  _board_location_to_dto(move_location)}


def exception_to_dto(api_exception):
    """ Maps an ApiException instance to a DTO to be transferred by the API """
    return {
        KEY: api_exception.key,
        MESSAGE: api_exception.message,
    }


def _player_to_dto(player: Player):
    """Maps a player to a DTO

    :param piece: an instance of model.Piece
    :return: a structure whose JSON representation is valid for the API
    """
    player_dto = {ID: player.identifier,
                  MAZE_CARD_ID: player.piece.maze_card.identifier}
    return player_dto


def _turns_to_next_player_action_dto(turns: Turns):
    """ Maps an instance of Turns to a DTO, representing
    only the next player's action.
    """
    next_player_action = turns.next_player_action()
    if not next_player_action:
        return None
    return {PLAYER_ID: next_player_action.player.identifier,
            ACTION: next_player_action.action}
