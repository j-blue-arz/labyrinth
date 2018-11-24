""" This module builds a Blueprint for the game api. It defines the API methods.
The module is responsible for request deserialization and result serialization, but
leaves DTO mapping, database manipulation and and domain logic access to the Service Layer """

from flask import Blueprint, request, json
import labyrinth.service as service

API = Blueprint('api', __name__, url_prefix='/api')


@API.errorhandler(service.ApiException)
def handle_api_exception(api_exception):
    """ maps the ApiException to an error response """
    return json.jsonify(api_exception.to_dto()), api_exception.status_code


@API.route('/games/<int:game_id>/players', methods=["POST"])
def post_player(game_id):
    """ Adds a player to an existing game. Creates the game if it does not exist """
    player_id = service.add_player(game_id)
    return json.jsonify(player_id)


@API.route('/games/<int:game_id>/state', methods=["GET"])
def get_state(game_id):
    """ Returns the state of the game for a player.
    The player id has to be given as a path parameter 'p_id'"""
    player_id = int(request.args["p_id"])
    return json.jsonify(service.get_game_state(game_id, player_id))


@API.route('/games/<int:game_id>/shift', methods=["POST"])
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
    service.perform_shift(game_id, player_id, request_body)
    return ""


@API.route('/games/<int:game_id>/move', methods=["POST"])
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
    service.perform_move(game_id, player_id, request_body)
    return ""
