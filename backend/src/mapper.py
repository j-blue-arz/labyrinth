""" Mapper implementation, maps between Model objects and Data Transfer Objects (DTOs).

There are no specific classes for these DTOs,
instead they are data structures built of dictionaries and lists,
which in turn are automatically translatable to structured text (JSON or XML)
"""
from model import Game

def map_game_state_to_dto(game):
    """Maps a game to a DTO

    :param game: an instance of model.Game
    :return: a structure whose JSON representation is valid for the API
    """
    

