import time
import json
import requests
from flask import Flask, url_for
from random import sample, choice
from .validation import MoveValidator
from .model import BoardLocation


class Computer:
    def __init__(self, game_id, game, player_id):
        self._game_id = game_id
        self._game = game
        maze = game.board.maze
        self._bfs = MoveValidator(maze)
        self._insert_locations = maze.insert_locations
        self._player_id = player_id

    def run(self):
        insert_location, insert_rotation, best_move = self._random_actions()
        time.sleep(2)
        self._post_shift(insert_location, insert_rotation)
        time.sleep(2)
        self._post_move(best_move)

    def _post_shift(self, insert_location, insert_rotation):
        dto = {}
        dto["location"] = _board_location_to_dto(insert_location)
        dto["leftoverRotation"] = insert_rotation
        requests.post(url_for("api.post_shift", game_id=self._game_id,
                              p_id=self._player_id, _external=True), json=dto)

    def _post_move(self, move_location):
        dto = {}
        dto["location"] = _board_location_to_dto(move_location)
        requests.post(url_for("api.post_move", game_id=self._game_id,
                              p_id=self._player_id, _external=True), json=dto)

    def _random_actions(self):
        def evaluate(location):
            return location.row - location.column

        piece = self._game.board.find_piece(self._player_id)
        piece_location = self._game.board.maze.maze_card_location(piece.maze_card)
        insert_location = sample(self._insert_locations, 1)[0]
        insert_rotation = choice([0, 90, 180, 270])
        reachable_locations = self._bfs.bfs(piece_location)
        best_move = piece_location
        for location in reachable_locations:
            if evaluate(location) > evaluate(best_move):
                best_move = location
        return insert_location, insert_rotation, best_move


def _board_location_to_dto(location: BoardLocation):
    """ Maps a board location to a DTO

    :param location: an instance of model.BoardLocation
    :return: a structure whose JSON representation is valid for the API
    """
    if location is None:
        return None
    return {"row": location.row,
            "column": location.column}
