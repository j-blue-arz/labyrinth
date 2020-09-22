""" Mapper implementation, maps between Model objects and Data Transfer Objects (DTOs).

There are no specific classes for these DTOs,
instead they are data structures built of dictionaries and lists,
which in turn are automatically translatable to structured text (JSON or XML)
"""
from labyrinth.model.game import Game, Turns, Player
import labyrinth.model.computer
from labyrinth.mapper.shared import _objective_to_dto, _dto_to_board_location, _board_location_to_dto, _board_to_dto
from labyrinth.mapper.constants import (ID, OBJECTIVE, PLAYERS, MAZE, NEXT_ACTION, ENABLED_SHIFT_LOCATIONS, LOCATION,
                                        MAZE_CARD_ID, LEFTOVER_ROTATION, KEY, MESSAGE, ACTION, PLAYER_ID,
                                        MAZE_SIZE, SCORE, PIECE_INDEX, IS_COMPUTER, COMPUTATION_METHOD)


def game_state_to_dto(game: Game):
    """Maps the game state, as served by the GET state request, to a DTO.
    Player ID is no longer a parameter, because with the change that all players have the same objective,
    every player has full information about the game.

    :param game: an instance of model.Game
    :return: a structure whose JSON representation is valid for the API
    """
    return {
        ID: game.identifier,
        OBJECTIVE: _objective_to_dto(game.board.objective_maze_card),
        PLAYERS: [player_to_dto(player) for player in game.players],
        MAZE: _board_to_dto(game.board),
        NEXT_ACTION: _turns_to_next_player_action_dto(game.turns),
        ENABLED_SHIFT_LOCATIONS: _enabled_shift_locations_to_dto(game)
    }


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


def dto_to_type(player_request_dto):
    """ Maps a DTO for the add player api method to the type of the player.

    More specifically, returns two values.  """
    if isinstance(player_request_dto, dict):
        is_computer = _value_or_false(player_request_dto, IS_COMPUTER)
        computation_method = _value_or_none(player_request_dto, COMPUTATION_METHOD)
        return is_computer, computation_method
    return False, None


def dto_to_maze_size(game_options_dto):
    """ Maps a DTO for the change game api method to a value for the size of the new maze """
    return game_options_dto[MAZE_SIZE]


def _value_or_none(dto, key):
    if key in dto:
        return dto[key]
    return None


def _value_or_false(dto, key):
    if key in dto:
        return dto[key]
    return False


def shift_action_to_dto(location, rotation):
    """ Maps a shift location and the rotation of the leftover maze card to a DTO, which is valid
    for the POST shift method of the API """
    return {"location":  _board_location_to_dto(location),
            "leftoverRotation": rotation}


def move_action_to_dto(move_location):
    """ Maps a location to a DTO, which is valid for the POST move method of the API """
    return {"location":  _board_location_to_dto(move_location)}


def exception_to_dto(api_exception):
    """ Maps an ApiException instance to a DTO to be transferred by the API """
    return {
        KEY: api_exception.key,
        MESSAGE: api_exception.message,
    }


def player_to_dto(player: Player):
    """Maps a player to a DTO

    :param piece: an instance of model.Piece
    :return: a structure whose JSON representation is valid for the API
    """
    player_dto = {ID: player.identifier,
                  MAZE_CARD_ID: player.piece.maze_card.identifier,
                  SCORE: player.score,
                  PIECE_INDEX: player.piece.piece_index}
    if type(player) is labyrinth.model.computer.ComputerPlayer:
        player_dto[IS_COMPUTER] = True
        player_dto[COMPUTATION_METHOD] = player.compute_method_factory.SHORT_NAME
    else:
        player_dto[IS_COMPUTER] = False
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


def _enabled_shift_locations_to_dto(game: Game):
    """ Maps the shift locations of the Board without the previous shift location of Game
    to a DTO.
    """
    return list(map(_board_location_to_dto, game.get_enabled_shift_locations()))
