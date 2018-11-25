""" Tests the api methods ( /api/ ) """
import json


def test_post_players(client):
    """ Tests POST for /api/games/0/players

    Expects an OK response with a single int in the body.
    """
    response = client.post("/api/games/0/players")
    assert response.content_type == "application/json"
    _assert_ok_single_int(response)


def test_post_players_four_times(client):
    """ Tests POST for /api/games/0/players

    Expects four OKs with pair-wise different numbers
    """
    player_ids = set()
    response = client.post("/api/games/0/players")
    player_ids.add(_assert_ok_single_int(response))
    response = client.post("/api/games/0/players")
    player_ids.add(_assert_ok_single_int(response))
    response = client.post("/api/games/0/players")
    player_ids.add(_assert_ok_single_int(response))
    response = client.post("/api/games/0/players")
    player_ids.add(_assert_ok_single_int(response))
    assert len(player_ids) == 4


def test_post_players_five_times(client):
    """ Tests POST for /api/games/0/players

    Expects four OKs
    and a 400 Bad Request with a exception body
    """
    response = client.post("/api/games/0/players")
    _assert_ok_single_int(response)
    response = client.post("/api/games/0/players")
    _assert_ok_single_int(response)
    response = client.post("/api/games/0/players")
    _assert_ok_single_int(response)
    response = client.post("/api/games/0/players")
    _assert_ok_single_int(response)
    response = client.post("/api/games/0/players")
    _assert_error_response(response, user_message="Number of players has reached game limit.",
                           key="GAME_FULL", status=400)


def test_get_state(client):
    """ Tests GET for /api/games/0/state

    for existing game. Expects 50 mazeCards and one player
    with correct id
    """
    player_id1 = _assert_ok_single_int(client.post("/api/games/0/players"))
    player_id2 = _assert_ok_single_int(client.post("/api/games/0/players"))
    response = client.get("/api/games/0/state?p_id={}".format(player_id2))
    assert response.status_code == 200
    assert response.content_type == "application/json"
    state = response.get_json()
    assert "mazeCards" in state
    assert len(state["mazeCards"]) == 50
    assert "players" in state
    assert len(state["players"]) == 2
    player_ids = {state["players"][0]["id"], state["players"][1]["id"]}
    assert player_ids == {player_id1, player_id2}


def test_get_state_for_nonexisting_game(client):
    """ Tests GET for /api/games/1/state

    for non-existing game. Expects 404 Not Found with
    exception body
    """
    player_id = _assert_ok_single_int(client.post("/api/games/0/players"))
    response = client.get("/api/games/1/state?p_id={}".format(player_id))
    _assert_error_response(response, user_message="The game does not exist.",
                           key="GAME_NOT_FOUND", status=404)


def test_get_state_for_nonexisting_player(client):
    """ Tests GET for /api/games/0/state

    for non-existing player. Expects 400 Bad Request with
    exception body
    """
    player_id = _assert_ok_single_int(client.post("/api/games/0/players"))
    response = client.get("/api/games/0/state?p_id={}".format(player_id + 1))
    _assert_error_response(response, user_message="The player does not take part in this game.",
                           key="PLAYER_NOT_IN_GAME", status=400)


def test_get_state_valid_after_error(client):
    """ Tests GET for /api/games/0/state

    after a previous request resulted in an error.
    Expects 200 OK
    """
    client.post("/api/games/0/players")
    client.post("/api/games/0/players")
    client.post("/api/games/0/players")
    response = client.post("/api/games/0/players")
    player_id = _assert_ok_single_int(response)
    response = client.post("/api/games/0/players")
    assert response.status_code == 400
    response = client.get("/api/games/0/state?p_id={}".format(player_id))
    assert response.status_code == 200
    assert response.content_type == "application/json"
    state = response.get_json()
    assert "mazeCards" in state
    assert len(state["mazeCards"]) == 50


def test_post_move(client):
    """ Tests POST for /api/games/0/move

    with correct request body.
    Expects a 200 OK, with empty body.
    State respects new position of player.
    """
    client.post("/api/games/0/players")
    response = client.post("/api/games/0/players")
    player_id = _assert_ok_single_int(response)
    data = json.dumps({
        "location": {
            "row": 4,
            "column": 3
        }
    })
    response = client.post("/api/games/0/move?p_id={}".format(player_id), data=data)
    assert response.status_code == 200
    assert response.content_length == 0
    response = client.get("/api/games/0/state?p_id={}".format(player_id))
    state = response.get_json()
    maze_card_id = next((player["mazeCardId"]
                         for player in state["players"] if player["id"] == player_id),
                        None)
    location = next((card["location"] for card in state["mazeCards"] if card["id"] == maze_card_id),
                    None)
    assert location["row"] == 4
    assert location["column"] == 3


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
    response = client.post("/api/games/0/players")
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
    response = client.post("/api/games/0/players")
    player_id = _assert_ok_single_int(response)
    old_state = client.get("/api/games/0/state?p_id={}".format(player_id)).get_json()
    old_leftover_card = next((card for card in old_state["mazeCards"] if card["location"] is None),
                             None)
    old_rotation = old_leftover_card["rotation"]
    new_rotation = (old_rotation + 180) % 360
    data = json.dumps({
        "location": {
            "row": 0,
            "column": 1
        },
        "leftoverRotation": new_rotation
    })
    response = client.post("/api/games/0/shift?p_id={}".format(player_id), data=data)
    assert response.status_code == 200
    assert response.content_length == 0
    new_state = client.get("/api/games/0/state?p_id={}".format(player_id)).get_json()
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


def _assert_invalid_action_and_unchanged_state(client, action_resource, data):
    """ Sets a game up, performs invalid action on given resource with given data,
    asserts error response and checks that state has not changed """
    response = client.post("/api/games/0/players")
    player_id = _assert_ok_single_int(response)
    response = client.get("/api/games/0/state?p_id={}".format(player_id))
    old_data = response.get_data()
    response = client.post("/api/games/0/{}?p_id={}".format(action_resource, player_id),
                           data=json.dumps(data))
    _assert_error_response(response, user_message="The sent action is invalid.",
                           key="INVALID_ACTION", status=400)
    response = client.get("/api/games/0/state?p_id={}".format(player_id))
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
