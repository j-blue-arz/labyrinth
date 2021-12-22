""" This module builds a Blueprint for the game api. It defines the API methods.
The module is responsible for request deserialization and result serialization, but
leaves DTO mapping, database manipulation and and domain logic access to the Controller """

from flask import Blueprint, request, json
from . import controller
from .exceptions import ApiException

API = Blueprint("api", __name__, url_prefix='/api')


@API.errorhandler(ApiException)
def handle_api_exception(api_exception):
    """ maps the ApiException to an error response """
    return api_exception.to_dto(), api_exception.status_code


@API.route("/games/<int:game_id>/players", methods=["POST"])
def post_player(game_id):
    """ Adds a player to an existing game. Creates the game if it does not exist.
    The request can contain a body of the form
    {
        'isBot': <boolean>,
        'computationMethod': <string>,
        'name': <string>
    }
    All fields are optional.
    """
    request_body = request.get_json(silent=True, force=True)
    return controller.add_player(game_id, request_body)


@API.route("/games/<int:game_id>/players/<int:player_id>", methods=["DELETE"])
def delete_player(game_id, player_id):
    """ Removes a player from a game. Game has to exist, player has to exist in game. """
    controller.delete_player(game_id, player_id)
    return ""


@API.route("/games/<int:game_id>/players/<int:player_id>/name", methods=["PUT"])
def rename_player(game_id, player_id):
    """ Changes the name of a player from a game. Game has to exist, player has to exist in game.
    Request body is expected to be
    {
        'name': <string>
    }
    """
    request_body = request.get_json(force=True)
    controller.change_player_name(game_id, player_id, request_body)
    return ""


@API.route("/games/<int:game_id>", methods=["PUT"])
def change_game(game_id):
    """ Changes game setup. The request has to contain a body of the form
    {
        'mazeSize': <number>
    },
    where mazeSize is the new size of the maze.
    """
    request_body = request.get_json(force=True)
    controller.change_game(game_id, request_body)
    return ""


@API.route("/games/<int:game_id>/state", methods=["GET"])
def get_state(game_id):
    """ Returns the state of the game """
    return controller.get_game_state(game_id)


@API.route("/games/<int:game_id>/shift", methods=["POST"])
def post_shift(game_id):
    """ Makes a shifting action for a player.
    The player id has to be given as a path parameter 'p_id'.
    The request body is expected to contain a JSON of the form
    {
        'location': {
            'row': <int>,
            'column': <int>
        },
        'leftoverRotation': <int>
    }"""
    player_id = int(request.args["p_id"])
    request_body = request.get_json(force=True)
    controller.perform_shift(game_id, player_id, request_body)
    return ""


@API.route("/games/<int:game_id>/move", methods=["POST"])
def post_move(game_id):
    """ Makes a move for a player.
    The player id has to be given as a path parameter 'p_id'.
    The request body is expected to contain a JSON of the form
    {
        'location': {
            'row': <int>
            'column': <int>
        }
    }"""
    player_id = int(request.args["p_id"])
    request_body = request.get_json(force=True)
    controller.perform_move(game_id, player_id, request_body)
    return ""


@API.route("/random-board", methods=["GET"])
def generate_board():
    requested_size = request.args.get("size", type=int)
    return controller.generate_board(size=requested_size)


@API.route("/computation-methods", methods=["GET"])
def get_computation_methods():
    """ Returns an array of available computation methods."""
    return json.jsonify(controller.get_computation_methods())
