""" Mapper implementation, maps between Model objects and persistable data structures (DTOs).

These DTOs are structures built of dictionaries and lists,
which in turn are automatically translatable to structured text (JSON or XML)
"""
from server.model.game import Game, Board, Piece, MazeCard, Turns, Maze, Player, PlayerAction
from server.model.computer import ComputerPlayer
from .shared import _objective_to_dto, _maze_cards_to_dto, _dto_to_board_location
from .constants import *


def game_to_dto(game: Game):
    """Maps a game to a DTO, which can be restored with dto_to_game()

    :param game: an instance of model.Game
    :return: a structure which can be encoded into JSON and decoded into a Game
    """
    game_dto = dict()
    game_dto[PLAYERS] = [_player_to_dto(player) for player in game.players]
    game_dto[MAZE_CARDS] = _maze_cards_to_dto(game.board)
    game_dto[NEXT_ACTION] = _turns_to_next_action_dto(game.turns)
    game_dto[OBJECTIVE] = _objective_to_dto(game.board.objective_maze_card)
    return game_dto


def dto_to_game(game_dto):
    """ maps a DTO to a game
    to deserialize a persisted instance.

    :param game_dto: a dictionary representing the structure of the game,
    created by game_to_dto
    :return: a Game instance whose state is equal to the DTO
    """
    maze = Maze()
    leftover_card = None
    maze_card_by_id = {}
    for maze_card_dto in game_dto[MAZE_CARDS]:
        maze_card, board_location = _dto_to_maze_card(maze_card_dto)
        if board_location is None:
            leftover_card = maze_card
        else:
            maze[board_location] = maze_card
        maze_card_by_id[maze_card.identifier] = maze_card
    objective_maze_card = maze_card_by_id[game_dto[OBJECTIVE]]
    board = Board(maze, leftover_card, objective_maze_card=objective_maze_card)
    players = [_dto_to_player(player_dto, 0, board, maze_card_by_id)
               for player_dto in game_dto[PLAYERS]]
    board._pieces = [player.piece for player in players]
    turns = _dto_to_turns(game_dto[NEXT_ACTION], players)
    game = Game(0, board=board, players=players, turns=turns)
    return game


def _player_to_dto(player: Player):
    """Maps a player to a DTO

    :param piece: an instance of model.Piece
    :return: a structure whose JSON representation is valid for the API
    """
    player_dto = {ID: player.identifier,
                  MAZE_CARD_ID: player.piece.maze_card.identifier}
    if type(player) is ComputerPlayer:
        player_dto[IS_COMPUTER] = True
        player_dto[ALGORITHM] = player.algorithm.SHORT_NAME
        player_dto[SHIFT_URL] = player.shift_url
        player_dto[MOVE_URL] = player.move_url
    return player_dto


def _turns_to_next_action_dto(turns: Turns):
    """ Maps an instance of Turns to a DTO, representing
    only the next action.
    """
    player_action = turns.next_player_action()
    if not player_action:
        return None
    return {PLAYER_ID: player_action.player.identifier,
            ACTION: player_action.action}


def _dto_to_player(player_dto, game_id, board, maze_card_dict):
    """ maps a DTO to a Player

    :param player: a dictionary representing game's (sub-)structure of a player,
    as created by _player_to_dto
    :param maze_card_dict: a dictionary between maze card ids and MazeCard instances
    :raises KeyError: if maze_card_dict does not contain the maze card or objective id in player_dto
    :return: a Player instance
    """
    piece = Piece(maze_card_dict[player_dto[MAZE_CARD_ID]])
    player = None
    if IS_COMPUTER in player_dto and player_dto[IS_COMPUTER]:
        player = ComputerPlayer(
            algorithm_name=player_dto[ALGORITHM],
            identifier=player_dto[ID],
            game_identifier=game_id,
            shift_url=player_dto[SHIFT_URL],
            move_url=player_dto[MOVE_URL],
            piece=piece)
    else:
        player = Player(identifier=player_dto[ID], game_identifier=game_id, piece=piece)
    player._board = board
    return player


def _dto_to_maze_card(maze_card_dto):
    """ Maps a DTO to a maze card and a board location

    :param maze_card_dto: a dictionary representing the game (sub-)structure of a maze card,
    as created by _maze_card_to_dto
    :return: a MazeCard instance and a BoardLocation instance (or None, for the leftover card)
    """
    maze_card = MazeCard(maze_card_dto[ID], maze_card_dto[DOORS], maze_card_dto[ROTATION])
    location = _dto_to_board_location(maze_card_dto[LOCATION])
    return maze_card, location


def _dto_to_turns(next_action_dto, players):
    """ Maps a DTO to a Turns instance

    :param next_action_dto: a dictionary representing the next player action,
    as created by _turns_to_next_action_dto
    :param players: a list of players. The value of the PLAYER_ID field in the dto
    has to match one of the player's id
    :return: an instance of Turns
    """
    if not players:
        return Turns()
    player = next(player for player in players if player.identifier == next_action_dto[PLAYER_ID])
    action = next_action_dto[ACTION]
    next_player_action = PlayerAction(player, action)
    return Turns(players, next_player_action)
