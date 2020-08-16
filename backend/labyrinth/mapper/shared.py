""" All methods and constants which are shared in persistence and dto """

from labyrinth.model.game import MazeCard, BoardLocation
from labyrinth.mapper.constants import ROW, COLUMN, ID, OUT_PATHS, ROTATION, LOCATION, MAZE_SIZE, MAZE_CARDS


def _objective_to_dto(maze_card: MazeCard):
    """ Maps a player's objective to a DTO

    :param maze_card: the player's objective MazeCard
    :return: the MazeCard's identifier, or None
    """
    if maze_card:
        return maze_card.identifier
    return None


def _board_location_to_dto(location: BoardLocation):
    """ Maps a board location to a DTO

    :param location: an instance of model.BoardLocation
    :return: a structure whose JSON representation is valid for the API
    """
    if location is None:
        return None
    return {ROW: location.row,
            COLUMN: location.column}


def _dto_to_board_location(board_location_dto):
    """ Maps a DTO to a board location

    :param board_location_dto: a dictionary for the game (sub-)structure of a board location, or None
    maps board location dtos created by _board_location_to_dto
    :return: a BoardLocation instance, or None
    """
    if board_location_dto is None:
        return None
    return BoardLocation(board_location_dto[ROW], board_location_dto[COLUMN])


def _maze_card_to_dto(maze_card: MazeCard, location: BoardLocation = None):
    """ Maps a maze card to a DTO

    :param maze_card: an instance of model.MazeCard
    :param location: an instance of BoardLocation, i.e. the location of this card in the maze.
    if no location is given, the card is not in the maze, i.e. it is the leftover card.
    :return: a structure whose JSON representation is valid for the API
    """
    return {ID: maze_card.identifier,
            OUT_PATHS: maze_card.out_paths,
            ROTATION: maze_card.rotation,
            LOCATION: _board_location_to_dto(location)}


def _maze_cards_to_dto(board):
    """ Maps all the given game's maze cards to one list of DTOs
    These include all cards in the maze and the leftover card with position None

    :param board: an instance of model.Board
    :return: a list of DTOs.
    """
    dto = []
    dto.append(_maze_card_to_dto(board.leftover_card, None))
    for location in board.maze.maze_locations:
        maze_card = board.maze[location]
        dto.append(_maze_card_to_dto(maze_card, location))
    return dto


def _board_to_dto(board):
    """ Maps the maze layout and the leftover card to a DTO.

    :param board: an instance of model.Board
    :return: a dictionary of the maze size and a list of maze card DTOs
    """
    dto = dict()
    dto[MAZE_SIZE] = board.maze.maze_size
    dto[MAZE_CARDS] = _maze_cards_to_dto(board)
    return dto
