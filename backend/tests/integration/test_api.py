""" Tests the api methods ( /api/ ) """
import json


def test_post_players(client):
    """ Tests POST for /api/games/0/players

    Expects an OK response with a single int in the body.
    """
    response = _post_player(client, player_type="human", alone=True)
    assert response.content_type == "application/json"
    _assert_ok_single_int(response)


def test_post_players_four_times(client):
    """ Tests POST for /api/games/0/players

    Expects four OKs with pair-wise different numbers
    """
    player_ids = set()
    response = _post_player(client, player_type="human", alone=True)
    player_ids.add(_assert_ok_single_int(response))
    response = _post_player(client, player_type="human", alone=True)
    player_ids.add(_assert_ok_single_int(response))
    response = _post_player(client, player_type="human", alone=True)
    player_ids.add(_assert_ok_single_int(response))
    response = _post_player(client, player_type="human", alone=True)
    player_ids.add(_assert_ok_single_int(response))
    assert len(player_ids) == 4


def test_post_players_five_times(client):
    """ Tests POST for /api/games/0/players

    Expects four OKs
    and a 400 Bad Request with a exception body
    """
    response = _post_player(client, player_type="human", alone=True)
    _assert_ok_single_int(response)
    response = _post_player(client, player_type="human", alone=True)
    _assert_ok_single_int(response)
    response = _post_player(client, player_type="human", alone=True)
    _assert_ok_single_int(response)
    response = _post_player(client, player_type="human", alone=True)
    _assert_ok_single_int(response)
    response = _post_player(client, player_type="human", alone=True)
    _assert_error_response(response, user_message="Number of players has reached game limit.",
                           key="GAME_FULL", status=400)


def test_get_state(client):
    """ Tests GET for /api/games/0/state

    for existing game. Expects 50 mazeCards and two players
    with correct id
    """
    player_id1 = _assert_ok_single_int(_post_player(client, player_type="human", alone=True))
    player_id2 = _assert_ok_single_int(_post_player(client, player_type="human", alone=True))
    response = _get_state(client, player_id2)
    assert response.status_code == 200
    assert response.content_type == "application/json"
    state = response.get_json()
    assert "mazeCards" in state
    assert len(state["mazeCards"]) == 50
    assert "players" in state
    assert len(state["players"]) == 2
    player_ids = {state["players"][0]["id"], state["players"][1]["id"]}
    assert player_ids == {player_id1, player_id2}


def test_get_state_has_correct_initial_state(client):
    """ Tests GET for /api/games/0/state

    for existing game. Expects players locations set to top left corner for first player.
    Expects top left corner to be a corner. Expects a single leftover card.
    Expects an objective to be set for the player
    """
    player_id = _assert_ok_single_int(_post_player(client, player_type="human", alone=True))
    response = _get_state(client, player_id)
    state = response.get_json()
    player_card_id = state["players"][0]["mazeCardId"]
    objective_card_id = state["objectiveMazeCardId"]
    player_maze_card = None
    objective_maze_card = None
    for maze_card in state["mazeCards"]:
        if maze_card["id"] == player_card_id:
            player_maze_card = maze_card
        if maze_card["id"] == objective_card_id:
            objective_maze_card = maze_card
    assert player_maze_card
    assert player_maze_card["location"]["row"] == 0
    assert player_maze_card["location"]["column"] == 0
    assert player_maze_card["doors"] == "NE"
    assert player_maze_card["rotation"] == 90
    assert objective_maze_card
    leftover_cards = [maze_card for maze_card in state["mazeCards"] if maze_card["location"] is None]
    assert len(leftover_cards) == 1
    leftover_card = leftover_cards[0]
    assert not "W" in leftover_card["doors"]
    assert "N" in leftover_card["doors"]


def test_get_state_for_nonexisting_game(client):
    """ Tests GET for /api/games/1/state

    for non-existing game. Expects 404 Not Found with
    exception body
    """
    player_id = _assert_ok_single_int(_post_player(client, player_type="human", alone=True))
    response = client.get("/api/games/1/state?p_id={}".format(player_id))
    _assert_error_response(response, user_message="The game does not exist.",
                           key="GAME_NOT_FOUND", status=404)


def test_get_state_for_nonexisting_player(client):
    """ Tests GET for /api/games/0/state

    for non-existing player. Expects 400 Bad Request with
    exception body
    """
    player_id = _assert_ok_single_int(_post_player(client, player_type="human", alone=True))
    response = _get_state(client, player_id + 1)
    _assert_error_response(response, user_message="The player does not take part in this game.",
                           key="PLAYER_NOT_IN_GAME", status=400)


def test_get_state_valid_after_error(client):
    """ Tests GET for /api/games/0/state

    after a previous request resulted in an error.
    Expects 200 OK
    """
    _post_player(client, player_type="human", alone=True)
    _post_player(client, player_type="human", alone=True)
    _post_player(client, player_type="human", alone=True)
    response = _post_player(client, player_type="human", alone=True)
    player_id = _assert_ok_single_int(response)
    response = _post_player(client, player_type="human", alone=True)
    assert response.status_code == 400
    response = _get_state(client, player_id)
    assert response.status_code == 200
    assert response.content_type == "application/json"
    state = response.get_json()
    assert "mazeCards" in state
    assert len(state["mazeCards"]) == 50


def test_post_move(client):
    """ Tests POST for /api/games/0/move

    with correct request body.
    The single player is placed on the top left corner. After pushing the leftover
    such that a move to the card to the right is possible, a move action is performed.
    It is exploited that every card has a "N" door.
    Expects a 200 OK, with empty body.
    State respects new position of player.
    """
    response = _post_player(client, player_type="human", alone=True)
    player_id = _assert_ok_single_int(response)
    _post_shift(client, player_id, 0, 1, 270)
    response = _post_move(client, player_id, 0, 1)
    assert response.status_code == 200
    assert response.content_length == 0
    response = _get_state(client, player_id)
    state = response.get_json()
    maze_card_id = next((player["mazeCardId"]
                         for player in state["players"] if player["id"] == player_id),
                        None)
    location = next((card["location"] for card in state["mazeCards"] if card["id"] == maze_card_id),
                    None)
    assert location["row"] == 0
    assert location["column"] == 1


def test_post_move_unreachable_move(client):
    """ Tests POST for /api/games/0/move

    with an unreachable location. The state is constructed by
    shifting the pieces next to the top left corner so that
    all outgoing paths are blocked.
    It is exploited that no card has a "W" door.
    Expects a 400 Bad Request, with exception body.
    State is unchanged.
    """
    response = _post_player(client, player_type="human", alone=True)
    player_id = _assert_ok_single_int(response)
    _post_shift(client, player_id, 0, 1, 0)
    _post_move(client, player_id, 0, 0)
    _post_shift(client, player_id, 1, 0, 90)
    response = _post_move(client, player_id, 0, 1)
    _assert_error_response(response, user_message="The sent action is invalid.",
                           key="INVALID_ACTION", status=400)


def test_post_move_invalid_move(client):
    """ Tests POST for /api/games/0/move

    with an invalid location.
    Expects a 400 Bad Request, with exception body.
    State is unchanged.
    """
    _assert_invalid_action_and_unchanged_state(client, "move", data={
        "location": {
            "row": 7,
            "column": 0
        }
    })


def test_post_move_nonexisting_game(client):
    """ Tests POST for /api/games/1/move

    for non-existing game and with invalid location.
    Expects 404 Not Found with exception body about not found game
    """
    response = _post_player(client, player_type="human", alone=True)
    player_id = _assert_ok_single_int(response)
    data = json.dumps({
        "location": {
            "row": 7,
            "column": 0
        }
    })
    response = client.post("/api/games/8/move?p_id={}".format(player_id), data=data)
    _assert_error_response(response, user_message="The game does not exist.",
                           key="GAME_NOT_FOUND", status=404)


def test_post_shift(client):
    """ Tests POST for /api/games/0/shift

    with correct request body.
    Expects a 200 OK, with empty body.
    State is correct about pushed in card with rotation.
    """
    response = _post_player(client, player_type="human", alone=True)
    player_id = _assert_ok_single_int(response)
    old_state = _get_state(client, player_id).get_json()
    old_leftover_card = next((card for card in old_state["mazeCards"] if card["location"] is None),
                             None)
    old_rotation = old_leftover_card["rotation"]
    new_rotation = (old_rotation + 180) % 360
    response = _post_shift(client, player_id, 0, 1, new_rotation)
    assert response.status_code == 200
    assert response.content_length == 0
    new_state = _get_state(client, player_id).get_json()
    old_leftover_card = next((card for card in old_state["mazeCards"] if card["location"] is None),
                             None)
    pushed_in_card = next((card for card in new_state["mazeCards"]
                           if card["id"] == old_leftover_card["id"]),
                          None)
    assert old_leftover_card["doors"] == pushed_in_card["doors"]
    assert pushed_in_card["rotation"] == new_rotation
    assert pushed_in_card["location"]["row"] == 0
    assert pushed_in_card["location"]["column"] == 1


def test_post_shift_with_invalid_rotation(client):
    """ Tests POST for /api/games/0/shift

    with invalid rotation.
    Expects a 400 Bad Request, with exception body.
    State is unchanged.
    """
    _assert_invalid_action_and_unchanged_state(client, "shift", data={
        "location": {
            "row": 0,
            "column": 1
        },
        "leftoverRotation": 66
    })


def test_post_shift_with_invalid_location(client):
    """ Tests POST for /api/games/0/shift

    with invalid rotation.
    Expects a 400 Bad Request, with exception body.
    State is unchanged.
    """
    _assert_invalid_action_and_unchanged_state(client, "shift", data={
        "location": {
            "row": 0,
            "column": 0
        },
        "leftoverRotation": 90
    })


def test_post_move_with_invalid_turn_action(client):
    """ Tests POST for /api/games/0/move

    when a shift should be performed.
    Expects a 400 Bad Request, with exception body.
    State is unchanged.
    """
    _assert_invalid_action_and_unchanged_state(client, "move", data={
        "location": {
            "row": 0,
            "column": 0
        }
    })


def test_turn_action_progression(client):
    """ Tests GET for /api/games/0/state

    expects the nextAction to change as correct actions are performed.
    """
    player_id_0 = _assert_ok_single_int(_post_player(client, player_type="human", alone=True))
    player_id_1 = _assert_ok_single_int(_post_player(client, player_type="human", alone=True))
    state = _get_state(client, player_id_0).get_json()
    assert state["nextAction"]["playerId"] == player_id_0
    assert state["nextAction"]["action"] == "SHIFT"
    _post_shift(client, player_id_0, 0, 1, 270)
    state = _get_state(client, player_id_0).get_json()
    assert state["nextAction"]["playerId"] == player_id_0
    assert state["nextAction"]["action"] == "MOVE"
    _post_move(client, player_id_0, 0, 0)
    state = _get_state(client, player_id_0).get_json()
    assert state["nextAction"]["playerId"] == player_id_1
    assert state["nextAction"]["action"] == "SHIFT"
    _post_shift(client, player_id_1, 0, 1, 270)
    state = _get_state(client, player_id_0).get_json()
    assert state["nextAction"]["playerId"] == player_id_1
    assert state["nextAction"]["action"] == "MOVE"
    _post_move(client, player_id_1, 0, 6)
    state = _get_state(client, player_id_0).get_json()
    assert state["nextAction"]["playerId"] == player_id_0
    assert state["nextAction"]["action"] == "SHIFT"


def test_delete_player(client):
    """ Tests GET for /api/games/0/state and delete for /api/games/0/players/<player_id>

    After a player was deleted, he should not be able to see the game state.
    """
    player_id_0 = _assert_ok_single_int(_post_player(client, player_type="human", alone=True))
    player_id_1 = _assert_ok_single_int(_post_player(client, player_type="human", alone=True))
    _delete_player(client, player_id_1)
    response = _get_state(client, player_id_1)
    _assert_error_response(response, user_message="The player does not take part in this game.",
                           key="PLAYER_NOT_IN_GAME", status=400)
    state = _get_state(client, player_id_0).get_json()
    assert len(state["players"]) == 1


def test_put_player(client):
    """ Tests PUT for /api/games/0/players/<player_id> and GET for /api/games/0/state

    Changes human player to computer player, expects state to respect this change
    """
    player_id_0 = _assert_ok_single_int(_post_player(client, player_type="human", alone=True))
    player_id_1 = _assert_ok_single_int(_post_player(client, player_type="human", alone=True))
    _put_player(client, player_id_1, player_type="random", alone=True)
    state = _get_state(client, player_id_0).get_json()
    assert len(state["players"]) == 2
    player = state["players"][1]
    assert "isComputerPlayer" in player
    assert player["isComputerPlayer"] is True
    assert player["algorithm"] == "random"
    assert player["id"] == player_id_1



def _assert_invalid_action_and_unchanged_state(client, action_resource, data):
    """ Sets a game up, performs invalid action on given resource with given data,
    asserts error response and checks that state has not changed """
    response = _post_player(client, player_type="human", alone=True)
    player_id = _assert_ok_single_int(response)
    response = _get_state(client, player_id)
    old_data = response.get_data()
    response = client.post("/api/games/0/{}?p_id={}".format(action_resource, player_id),
                           data=json.dumps(data))
    _assert_error_response(response, user_message="The sent action is invalid.",
                           key="INVALID_ACTION", status=400)
    response = _get_state(client, player_id)
    assert response.status_code == 200
    new_data = response.get_data()
    assert old_data == new_data


def _assert_ok_single_int(response):
    """ Asserts that a response has a 200 OK status,
    a single int in the body
    """
    assert response.status_code == 200
    try:
        return int(response.get_data())
    except ValueError:
        assert False


def _assert_error_response(response, user_message, key, status):
    """ Asserts a certain error response

    :param response: the HTTP response object
    :param user_message: a human readable explanation for the error
    :param key: an error key, to be used for i18n
    :param status: the expected status code
    """
    assert response.status_code == status
    assert response.content_type == "application/json"
    message = response.get_json()
    assert message["userMessage"] == user_message
    assert message["key"] == key


def _post_shift(client, player_id, row, column, rotation):
    """ performs a shift API operation with the given parameters """
    data = json.dumps({
        "location": {
            "row": row,
            "column": column
        },
        "leftoverRotation": rotation
    })
    return client.post("/api/games/0/shift?p_id={}".format(player_id), data=data, mimetype="application/json")


def _post_move(client, player_id, row, column):
    data = json.dumps({
        "location": {
            "row": row,
            "column": column
        }
    })
    return client.post("/api/games/0/move?p_id={}".format(player_id), data=data, mimetype="application/json")


def _post_player(client, player_type=None, alone=None):
    player_data = _player_data(player_type, alone)
    return client.post("/api/games/0/players", data=player_data, mimetype="application/json")

def _delete_player(client, player_id):
    return client.delete("/api/games/0/players/{}".format(player_id))

def _put_player(client, player_id, player_type=None, alone=None):
    player_data = _player_data(player_type, alone)
    return client.put("/api/games/0/players/{}".format(player_id), data=player_data, mimetype="application/json")

def _get_state(client, player_id):
    return client.get("/api/games/0/state?p_id={}".format(player_id))

def _player_data(player_type=None, alone=None):
    data = None
    if alone is not None and player_type is not None:
        data = {
            "type": player_type,
            "alone": alone
        }
    elif alone is not None:
        data = {
            "alone": alone
        }
    elif player_type is not None:
        data = {
            "type": player_type
        }
    if data:
        data = json.dumps(data)
    return data
