""" Tests the api methods ( /api/ ) """
import json


def test_post_players_four_times(client):
    """ Tests POST for /api/games/0/players

    Expects four OKs with pair-wise different numbers
    """
    player_ids = set()
    response = _post_player(client, player_type="human")
    player_ids.add(_assert_ok_single_int(response))
    response = _post_player(client, player_type="human")
    player_ids.add(_assert_ok_single_int(response))
    response = _post_player(client, player_type="human")
    player_ids.add(_assert_ok_single_int(response))
    response = _post_player(client, player_type="human")
    player_ids.add(_assert_ok_single_int(response))
    assert len(player_ids) == 4


def test_post_players_backend_computer_player(client):
    """ Tests POST for /api/games/0/players with computer player

    Adds a human player and a computer player with compute method 'random'
    Expects an OK response with a single int in the body.
    Checks if the game state respects the added computer player.
    """
    _post_player(client, player_type="human")
    response = _post_player(client, player_type="random")
    assert response.content_type == "application/json"
    _assert_ok_single_int(response)
    response = _get_state(client)
    state = response.get_json()
    assert len(state["players"]) == 2
    assert state["players"][1]["isComputerPlayer"] is True
    assert state["players"][1]["algorithm"] == "random"


def test_post_players_library_computer_player(client):
    """ Tests POST for /api/games/0/players with computer player

    Adds a human player and a computer player with compute method 'dynamic-libexhsearch'
    Expects an OK response with a single int in the body.
    Checks if the game state respects the added computer player.
    """
    _post_player(client, player_type="human")
    response = _post_player(client, player_type="dynamic-libexhsearch")
    assert response.content_type == "application/json"
    _assert_ok_single_int(response)
    response = _get_state(client)
    state = response.get_json()
    assert state["players"][1]["isComputerPlayer"] is True
    assert state["players"][1]["algorithm"] == "dynamic-libexhsearch"


def test_post_players_unknown_compute_method(client):
    """ Tests POST for /api/games/0/players

    Expects an 400 response with the requested compute method in the message.
    """
    response = _post_player(client, player_type="FOO")
    _assert_error_response(response, user_message_contains="FOO", key="INVALID_ARGUMENTS", status=400)


def test_post_players_five_times(client):
    """ Tests POST for /api/games/0/players

    Expects four OKs
    and a 400 Bad Request with a exception body
    """
    response = _post_player(client, player_type="human")
    _assert_ok_single_int(response)
    response = _post_player(client, player_type="human")
    _assert_ok_single_int(response)
    response = _post_player(client, player_type="human")
    _assert_ok_single_int(response)
    response = _post_player(client, player_type="human")
    _assert_ok_single_int(response)
    response = _post_player(client, player_type="human")
    _assert_error_response(response, user_message="Number of players has reached game limit.",
                           key="GAME_FULL", status=400)


def test_get_state(client):
    """ Tests GET for /api/games/0/state

    for existing game. Expects 50 mazeCards and two players
    with correct id
    """
    player_id1 = _assert_ok_single_int(_post_player(client, player_type="human"))
    player_id2 = _assert_ok_single_int(_post_player(client, player_type="human"))
    response = _get_state(client)
    assert response.status_code == 200
    assert response.content_type == "application/json"
    state = response.get_json()
    assert "maze" in state
    assert "mazeSize" in state["maze"]
    assert state["maze"]["mazeSize"] == 7
    assert "mazeCards" in state["maze"]
    assert len(state["maze"]["mazeCards"]) == 50
    assert "players" in state
    assert len(state["players"]) == 2
    player_ids = {state["players"][0]["id"], state["players"][1]["id"]}
    assert player_ids == {player_id1, player_id2}


def test_post_player_creates_game_with_correct_identifier(client):
    """ Tests POST for /api/games/3/players

    Expects an OK response with a single int in the body.
    Expects a game to be created with identifier 3
    """
    _post_player(client, game_id=3)
    response = _get_state(client, game_id=3)
    state = response.get_json()
    assert state["id"] == 3


def test_get_state_has_correct_initial_state(client):
    """ Tests GET for /api/games/0/state

    for existing game. Expects players locations set to top left corner for first player.
    Expects top left corner to be a corner. Expects a single leftover card.
    Expects an objective to be set for the player.
    Expects scores to be set to 0.
    """
    _assert_ok_single_int(_post_player(client, player_type="human"))
    response = _get_state(client)
    state = response.get_json()
    player_card_id = state["players"][0]["mazeCardId"]
    objective_card_id = state["objectiveMazeCardId"]
    player_maze_card = None
    objective_maze_card = None
    for maze_card in state["maze"]["mazeCards"]:
        if maze_card["id"] == player_card_id:
            player_maze_card = maze_card
        if maze_card["id"] == objective_card_id:
            objective_maze_card = maze_card
    assert player_maze_card
    assert player_maze_card["location"]["row"] == 0
    assert player_maze_card["location"]["column"] == 0
    assert player_maze_card["outPaths"] == "NE"
    assert player_maze_card["rotation"] == 90
    assert objective_maze_card
    leftover_cards = [maze_card for maze_card in state["maze"]["mazeCards"] if maze_card["location"] is None]
    assert len(leftover_cards) == 1
    leftover_card = leftover_cards[0]
    assert "W" not in leftover_card["outPaths"]
    assert "N" in leftover_card["outPaths"]
    for player in state["players"]:
        assert player["score"] == 0


def test_get_state_for_nonexisting_game(client):
    """ Tests GET for /api/games/1/state

    for non-existing game. Expects 404 Not Found with
    exception body
    """
    _assert_ok_single_int(_post_player(client, player_type="human"))
    response = client.get("/api/games/1/state")
    _assert_error_response(response, user_message="The game does not exist.",
                           key="GAME_NOT_FOUND", status=404)


def test_get_state_valid_after_error(client):
    """ Tests GET for /api/games/0/state

    after a previous request resulted in an error.
    Expects 200 OK
    """
    _post_player(client, player_type="human")
    _post_player(client, player_type="human")
    _post_player(client, player_type="human")
    response = _post_player(client, player_type="human")
    _assert_ok_single_int(response)
    response = _post_player(client, player_type="human")
    assert response.status_code == 400
    response = _get_state(client)
    assert response.status_code == 200
    assert response.content_type == "application/json"
    state = response.get_json()
    assert "mazeCards" in state["maze"]
    assert len(state["maze"]["mazeCards"]) == 50


def test_change_maze_size(client):
    """ Tests PUT for /api/games/0

    Creates a game, then increases maze size.
    Checks number of maze cards.
    """
    _post_player(client, game_id=5)
    _post_player(client, game_id=5)
    response = _put_game(client, game_id=5, size=11)
    assert response.status_code == 200
    response = _get_state(client, game_id=5)
    state = response.get_json()
    assert state["maze"]["mazeSize"] == 11
    assert len(state["maze"]["mazeCards"]) == 11*11 + 1


def test_change_maze_size_with_even_size(client):
    """ Tests PUT for /api/games/0

    With even size, the expectation is an exception.
    """
    _post_player(client, game_id=5)
    response = _put_game(client, game_id=5, size=12)
    _assert_error_response(response, user_message="The combination of arguments in this request is not supported.",
                           key="INVALID_ARGUMENTS", status=400)


def test_post_move(client):
    """ Tests POST for /api/games/0/move

    with correct request body.
    The single player is placed on the top left corner. After pushing the leftover
    such that a move to the card to the right is possible, a move action is performed.
    It is exploited that every card has a "N" out_path.
    Expects a 200 OK, with empty body.
    State respects new position of player.
    """
    response = _post_player(client, player_type="human")
    player_id = _assert_ok_single_int(response)
    _post_shift(client, player_id, 0, 1, 270)
    response = _post_move(client, player_id, 0, 1)
    assert response.status_code == 200
    assert response.content_length == 0
    response = _get_state(client)
    state = response.get_json()
    maze_card_id = next((player["mazeCardId"]
                         for player in state["players"] if player["id"] == player_id),
                        None)
    location = next((card["location"] for card in state["maze"]["mazeCards"] if card["id"] == maze_card_id),
                    None)
    assert location["row"] == 0
    assert location["column"] == 1


def test_post_move_unreachable_move(client):
    """ Tests POST for /api/games/0/move

    with an unreachable location. The state is constructed by
    shifting the pieces next to the top left corner so that
    all outgoing paths are blocked.
    It is exploited that no card has a "W" out_path.
    Expects a 400 Bad Request, with exception body.
    State is unchanged.
    """
    response = _post_player(client, player_type="human")
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
    response = _post_player(client, player_type="human")
    player_id = _assert_ok_single_int(response)
    _assert_invalid_action_and_unchanged_state(client, lambda: _post_move(client, player_id, 7, 0))


def test_post_move_nonexisting_game(client):
    """ Tests POST for /api/games/1/move

    for non-existing game and with invalid location.
    Expects 404 Not Found with exception body about not found game
    """
    response = _post_player(client, player_type="human")
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
    response = _post_player(client, player_type="human")
    player_id = _assert_ok_single_int(response)
    old_state = _get_state(client).get_json()
    old_leftover_card = next((card for card in old_state["maze"]["mazeCards"] if card["location"] is None),
                             None)
    old_rotation = old_leftover_card["rotation"]
    new_rotation = (old_rotation + 180) % 360
    response = _post_shift(client, player_id, 0, 1, new_rotation)
    assert response.status_code == 200
    assert response.content_length == 0
    new_state = _get_state(client).get_json()
    old_leftover_card = next((card for card in old_state["maze"]["mazeCards"] if card["location"] is None),
                             None)
    pushed_in_card = next((card for card in new_state["maze"]["mazeCards"]
                           if card["id"] == old_leftover_card["id"]),
                          None)
    assert old_leftover_card["outPaths"] == pushed_in_card["outPaths"]
    assert pushed_in_card["rotation"] == new_rotation
    assert pushed_in_card["location"]["row"] == 0
    assert pushed_in_card["location"]["column"] == 1


def test_post_shift_with_invalid_rotation(client):
    """ Tests POST for /api/games/0/shift

    with invalid rotation.
    Expects a 400 Bad Request, with exception body.
    State is unchanged.
    """
    response = _post_player(client, player_type="human")
    player_id = _assert_ok_single_int(response)
    _assert_invalid_argument_and_unchanged_state(client, lambda: _post_shift(client, player_id, 0, 1, 66))


def test_post_shift_with_invalid_location(client):
    """ Tests POST for /api/games/0/shift

    with invalid rotation.
    Expects a 400 Bad Request, with exception body.
    State is unchanged.
    """
    response = _post_player(client, player_type="human")
    player_id = _assert_ok_single_int(response)
    _assert_invalid_action_and_unchanged_state(client, lambda: _post_shift(client, player_id, 0, 0, 90))


def test_post_move_with_invalid_turn_action(client):
    """ Tests POST for /api/games/0/move

    when a shift should be performed.
    Expects a 400 Bad Request, with exception body.
    State is unchanged.
    """
    response = _post_player(client, player_type="human")
    player_id = _assert_ok_single_int(response)
    _assert_invalid_action_and_unchanged_state(client, lambda: _post_move(client, player_id, 0, 0))


def test_turn_action_progression(client):
    """ Tests GET for /api/games/0/state

    expects the nextAction to change as correct actions are performed.
    """
    player_id_0 = _assert_ok_single_int(_post_player(client, player_type="human"))
    player_id_1 = _assert_ok_single_int(_post_player(client, player_type="human"))
    state = _get_state(client).get_json()
    assert state["nextAction"]["playerId"] == player_id_0
    assert state["nextAction"]["action"] == "SHIFT"
    _post_shift(client, player_id_0, 0, 1, 270)
    state = _get_state(client).get_json()
    assert state["nextAction"]["playerId"] == player_id_0
    assert state["nextAction"]["action"] == "MOVE"
    _post_move(client, player_id_0, 0, 0)
    state = _get_state(client).get_json()
    assert state["nextAction"]["playerId"] == player_id_1
    assert state["nextAction"]["action"] == "SHIFT"
    _post_shift(client, player_id_1, 0, 1, 270)
    state = _get_state(client).get_json()
    assert state["nextAction"]["playerId"] == player_id_1
    assert state["nextAction"]["action"] == "MOVE"
    _post_move(client, player_id_1, 0, 6)
    state = _get_state(client).get_json()
    assert state["nextAction"]["playerId"] == player_id_0
    assert state["nextAction"]["action"] == "SHIFT"


def test_no_pushback_rule(client):
    """ Tests POST for /api/games/0/shift

    expects the second shift, which tries to revert the previous shift, to fail
    """
    player_id_0 = _assert_ok_single_int(_post_player(client, player_type="human"))
    player_id_1 = _assert_ok_single_int(_post_player(client, player_type="human"))
    _post_shift(client, player_id_0, 0, 1, 270)
    _post_move(client, player_id_0, 0, 0)
    _assert_invalid_action_and_unchanged_state(client, lambda: _post_shift(client, player_id_1, 6, 1, 270))


def test_delete_player(client):
    """ Tests GET for /api/games/0/state and delete for /api/games/0/players/<player_id>

    After a player was deleted, he should not be able to see the game state.
    """
    _post_player(client, player_type="human")
    player_id_1 = _assert_ok_single_int(_post_player(client, player_type="human"))
    _delete_player(client, player_id_1)
    state = _get_state(client).get_json()
    assert len(state["players"]) == 1


def _assert_invalid_argument_and_unchanged_state(client, action_callable):
    _assert_error_response_and_unchanged_state(
        client, action_callable, expected_user_message="The combination of arguments in this request is not supported.",
        expected_key="INVALID_ARGUMENTS")


def _assert_invalid_action_and_unchanged_state(client, action_callable):
    _assert_error_response_and_unchanged_state(
        client, action_callable, expected_user_message="The sent action is invalid.", expected_key="INVALID_ACTION")


def _assert_error_response_and_unchanged_state(client, action_callable, expected_user_message, expected_key):
    """ Sets a game up, performs invalid action on given resource with given data,
    asserts error response and checks that state has not changed """
    response = _get_state(client)
    old_data = response.get_data()
    response = action_callable()
    _assert_error_response(response, user_message=expected_user_message,
                           key=expected_key, status=400)
    response = _get_state(client)
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


def _assert_error_response(response, key, status, user_message=None, user_message_contains=None):
    """ Asserts a certain error response

    :param response: the HTTP response object
    :param user_message: a human readable explanation for the error
    :param key: an error key, to be used for i18n
    :param status: the expected status code
    """
    assert response.status_code == status
    assert response.content_type == "application/json"
    message = response.get_json()
    if user_message:
        assert message["userMessage"] == user_message
    if user_message_contains:
        assert user_message_contains in message["userMessage"]
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


def _post_player(client, player_type=None, game_id=0):
    player_data = _player_data(player_type)
    return client.post("/api/games/{}/players".format(game_id), data=player_data, mimetype="application/json")


def _delete_player(client, player_id):
    return client.delete("/api/games/0/players/{}".format(player_id))


def _put_game(client, game_id=0, size=7):
    game_data = None
    if size:
        game_data = json.dumps({"mazeSize": size})
    return client.put("/api/games/{}".format(game_id), data=game_data, mimetype="application/json")


def _get_state(client, game_id=0):
    return client.get("/api/games/{}/state".format(game_id))


def _player_data(player_type=None):
    data = None
    if player_type is not None:
        data = {
            "type": player_type
        }
    if data:
        data = json.dumps(data)
    return data
