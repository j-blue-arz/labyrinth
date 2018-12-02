""" Mapper implementation, maps between Model objects and Data Transfer Objects (DTOs).

There are no specific classes for these DTOs,
instead they are data structures built of dictionaries and lists,
which in turn are automatically translatable to structured text (JSON or XML)
"""
from .domain.model import Game, Player, MazeCard, BoardLocation, Board
#from labyrinth.service import ApiException

_PLAYERS = "players"
_MAZE_CARDS = "mazeCards"
_ID = "id"
_MAZE_CARD_ID = "mazeCardId"
_DOORS = "doors"
_LOCATION = "location"
_ROTATION = "rotation"
_ROW = "row"
_COLUMN = "column"
_LEFTOVER_ROTATION = "leftoverRotation"
_KEY = "key"
_MESSAGE = "userMessage"
_OBJECTIVE = "objectiveMazeCardId"


def player_state_to_dto(game: Game, player_id):
    """Maps a game, as seen from one player, to a DTO.

    :param game: an instance of model.Game
    :param player_id: the identifier of the player.
    :return: a structure whose JSON representation is valid for the API
    """
    game_dto = dict()
    game_dto[_PLAYERS] = [_player_to_dto(player) for player in game.players]
    game_dto[_MAZE_CARDS] = _maze_cards_to_dto(game)
    game_dto[_OBJECTIVE] = _objective_to_dto(game.find_player(player_id).objective_maze_card)
    return game_dto


def game_to_dto(game: Game):
    """Maps a game to a DTO, which can be restored with dto_to_game()

    :param game: an instance of model.Game
    :param player_id: an identifier of a player.
    If given, only returns the state from the view of the player.
    :return: a structure which can be encoded into JSON. 
    """
    game_dto = dict()
    game_dto[_PLAYERS] = [_player_to_dto(player, include_objective=True) for player in game.players]
    game_dto[_MAZE_CARDS] = _maze_cards_to_dto(game)
    return game_dto

def dto_to_game(game_dto):
    """ maps a DTO to a game
    to deserialize a persisted instance.

    :param game_dto: a dictionary representing the structure of the game,
    created by game_to_dto
    :return: a Game instance whose state is equal to the DTO
    """
    game = Game()
    maze_card_by_id = {}
    for maze_card_dto in game_dto[_MAZE_CARDS]:
        maze_card, board_location = _dto_to_maze_card(maze_card_dto)
        if board_location is None:
            game.leftover_card = maze_card
        else:
            game.board[board_location] = maze_card
        maze_card_by_id[maze_card.identifier] = maze_card
    game.players = [_dto_to_player(player_dto, maze_card_by_id)
                    for player_dto in game_dto[_PLAYERS]]
    return game


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
    return _dto_to_board_location(shift_dto[_LOCATION]), shift_dto[_LEFTOVER_ROTATION]


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
    return _dto_to_board_location(move_dto[_LOCATION])


def exception_to_dto(api_exception):
    """ Maps an ApiException instance to a DTO to be transferred by the API """
    return {
        _KEY: api_exception.key,
        _MESSAGE: api_exception.message,
    }


def _player_to_dto(player: Player, include_objective=False):
    """Maps a player to a DTO

    :param player: an instance of model.Player
    :param include_objective: if True, includes the player's objective_maze_card in the DTO
    :return: a structure whose JSON representation is valid for the API
    """
    player_dto = {_ID: player.identifier,
                  _MAZE_CARD_ID: player.maze_card.identifier}
    if include_objective:
        player_dto[_OBJECTIVE] = _objective_to_dto(player.objective_maze_card)
    return player_dto


def _objective_to_dto(maze_card: MazeCard):
    """ Maps a player's objective to a DTO

    :param maze_card: the player's objective MazeCard
    :return: the MazeCard's identifier, or None
    """
    if maze_card:
        return maze_card.identifier
    return None


def _maze_card_to_dto(maze_card: MazeCard, location: BoardLocation = None):
    """ Maps a maze card to a DTO

    :param maze_card: an instance of model.MazeCard
    :param location: an instance of BoardLocation, i.e. the location of this card on the board.
    if no location is given, the card is not on the board, i.e. it is the leftover card.
    :return: a structure whose JSON representation is valid for the API
    """
    return {_ID: maze_card.identifier,
            _DOORS: maze_card.doors,
            _ROTATION: maze_card.rotation,
            _LOCATION: _board_location_to_dto(location)}

def _maze_cards_to_dto(game):
    """ Maps all the given game's maze cards to one list of DTOs
    These include all cards on the board and the leftover card with position None

    :param game: an instance of model.Game
    :return: a list of DTOs.
    """
    dto = []
    dto.append(_maze_card_to_dto(game.leftover_card, None))
    for location in game.board.board_locations():
        maze_card = game.board[location]
        dto.append(_maze_card_to_dto(maze_card, location))
    return dto

def _board_location_to_dto(location: BoardLocation):
    """ Maps a board location to a DTO

    :param location: an instance of model.BoardLocation
    :return: a structure whose JSON representation is valid for the API
    """
    if location is None:
        return None
    return {_ROW: location.row,
            _COLUMN: location.column}


def _dto_to_player(player_dto, maze_card_dict):
    """ maps a DTO to a player

    :param player_dto: a dictionary representing game's (sub-)structure of a player,
    as created by _player_to_dto
    :param maze_card_dict: a dictionary between maze card ids and MazeCard instances
    :raises KeyError: if maze_card_dict does not contain the maze card or objective id in player_dto
    :return: a Player instance
    """
    player = Player(player_dto[_ID], maze_card_dict[player_dto[_MAZE_CARD_ID]])
    if player_dto[_OBJECTIVE]:
        player.objective_maze_card = maze_card_dict[player_dto[_OBJECTIVE]]
    return player


def _dto_to_maze_card(maze_card_dto):
    """ Maps a DTO to a maze card and a board location

    :param maze_card_dto: a dictionary representing the game (sub-)structure of a maze card,
    as created by _maze_card_to_dto
    :return: a MazeCard instance and a BoardLocation instance (or None, for the leftover card)
    """
    maze_card = MazeCard(maze_card_dto[_ID], maze_card_dto[_DOORS], maze_card_dto[_ROTATION])
    location = _dto_to_board_location(maze_card_dto[_LOCATION])
    return maze_card, location


def _dto_to_board_location(board_location_dto):
    """ Maps a DTO to a board location

    :param board_location_dto: a dictionary for the game (sub-)structure of a board location, or None
    maps board location dtos created by _board_location_to_dto
    :return: a BoardLocation instance, or None
    """
    if board_location_dto is None:
        return None
    return BoardLocation(board_location_dto[_ROW], board_location_dto[_COLUMN])
