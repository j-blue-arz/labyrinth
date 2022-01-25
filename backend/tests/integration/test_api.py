""" Tests the api methods ( /api/ ) """
from datetime import timedelta
import json
import os
import time


def test_post_player_returns_player(client):
    """ Tests POST for /api/games/0/players """
    response = _post_player(client)
    assert response.status_code == 200
    player = response.get_json()
    assert player["id"] >= 0
    assert player["isBot"] is False
    assert "pieceIndex" in player
    assert player["pieceIndex"] >= 0
    _wait_for(client, "SHIFT")


def test_post_players_four_times(client):
    """ Tests POST for /api/games/0/players

    Expects four OKs with pair-wise different numbers
    """
    player_ids = set()
    response = _post_player(client)
    player_ids.add(_assert_ok_retrieve_id(response))
    response = _post_player(client)
    player_ids.add(_assert_ok_retrieve_id(response))
    response = _post_player(client)
    player_ids.add(_assert_ok_retrieve_id(response))
    response = _post_player(client)
    player_ids.add(_assert_ok_retrieve_id(response))
    assert len(player_ids) == 4
    _wait_for(client, "SHIFT")


def test_post_players_library_bot(client):
    """ Tests POST for /api/games/0/players with bot

    Adds a human player and a bot with compute method 'libexhsearch'
    Expects an OK response with a single int in the body.
    Checks if the game state respects the added bot.
    """
    _post_player(client)
    response = _post_player(client, is_bot=True, computation_method="libexhsearch")
    assert response.content_type == "application/json"
    _assert_ok_retrieve_id(response)
    response = _get_state(client)
    state = response.get_json()
    assert state["players"][1]["isBot"] is True
    assert state["players"][1]["computationMethod"] == "libexhsearch"
    _wait_for(client, "SHIFT")


def test_post_players_unknown_compute_method(client):
    """ Tests POST for /api/games/0/players

    Expects an 400 response with the requested compute method in the message.
    """
    response = _post_player(client, is_bot=True, computation_method="FOO")
    _assert_error_response(response, user_message_contains="FOO", key="INVALID_ARGUMENTS", status=400)


def test_post_players_five_times(client):
    """ Tests POST for /api/games/0/players

    Expects four OKs
    and a 400 Bad Request with a exception body
    """
    response = _post_player(client)
    _assert_ok_retrieve_id(response)
    response = _post_player(client)
    _assert_ok_retrieve_id(response)
    response = _post_player(client)
    _assert_ok_retrieve_id(response)
    response = _post_player(client)
    _assert_ok_retrieve_id(response)
    response = _post_player(client)
    _assert_error_response(response, user_message="Number of players has reached game limit.",
                           key="GAME_FULL", status=400)
    _wait_for(client, "SHIFT")


def test_delete_player(client):
    """ Tests GET for /api/games/0/state and delete for /api/games/0/players/<player_id>

    After a player was deleted, he should not be able to see the game state.
    """
    _post_player(client)
    player_id_1 = _assert_ok_retrieve_id(_post_player(client))
    _delete_player(client, player_id_1)
    state = _get_state(client).get_json()
    assert len(state["players"]) == 1
    _wait_for(client, "SHIFT")


def test_player_name(client):
    """ Tests creating a player without a specific name """
    _post_player(client)
    state = _get_state(client).get_json()
    assert "name" not in state["players"][0]


def test_name_player(client):
    """ Tests giving a name to a created player """
    _post_player(client, name="myname")
    state = _get_state(client).get_json()
    assert state["players"][0]["name"] == "myname"


def test_rename_player(client):
    """ Tests PUT for /api/games/0/player/<player_id> to rename a player """
    player_id = _assert_ok_retrieve_id(_post_player(client, name="myname"))
    _put_player_name(client, player_id, name="anothername")
    state = _get_state(client).get_json()
    assert state["players"][0]["name"] == "anothername"


def test_get_state(client):
    """ Tests GET for /api/games/0/state

    for existing game. Expects 50 mazeCards and two players
    with correct id
    """
    player_id1 = _assert_ok_retrieve_id(_post_player(client))
    player_id2 = _assert_ok_retrieve_id(_post_player(client))
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
    _wait_for(client, "SHIFT")


def test_post_player_creates_game_with_correct_identifier(client):
    """ Tests POST for /api/games/3/players

    Expects an OK response with a single int in the body.
    Expects a game to be created with identifier 3
    """
    _post_player(client, game_id=3)
    response = _get_state(client, game_id=3)
    state = response.get_json()
    assert state["id"] == 3
    _wait_for(client, "SHIFT", game_id=3)


def test_get_state_has_correct_initial_state(client):
    """ Tests GET for /api/games/0/state

    for existing game. Expects players locations set to top left corner for first player.
    Expects top left corner to be a corner. Expects a single leftover card.
    Expects an objective to be set for the player.
    Expects scores to be set to 0.
    """
    _assert_ok_retrieve_id(_post_player(client))
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
    _wait_for(client, "SHIFT")


def test_get_state_for_nonexisting_game(client):
    """ Tests GET for /api/games/1/state

    for non-existing game. Expects 404 Not Found with
    exception body
    """
    _assert_ok_retrieve_id(_post_player(client))
    response = client.get("/api/games/1/state")
    _assert_error_response(response, user_message="The game does not exist.",
                           key="GAME_NOT_FOUND", status=404)
    _wait_for(client, "SHIFT")


def test_get_state_valid_after_error(client):
    """ Tests GET for /api/games/0/state

    after a previous request resulted in an error.
    Expects 200 OK
    """
    _post_player(client)
    _post_player(client)
    _post_player(client)
    response = _post_player(client)
    _assert_ok_retrieve_id(response)
    response = _post_player(client)
    assert response.status_code == 400
    response = _get_state(client)
    assert response.status_code == 200
    assert response.content_type == "application/json"
    state = response.get_json()
    assert "mazeCards" in state["maze"]
    assert len(state["maze"]["mazeCards"]) == 50
    _wait_for(client, "SHIFT")


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
    _wait_for(client, "SHIFT", game_id=5)


def test_change_maze_size_with_even_size(client):
    """ Tests PUT for /api/games/0

    With even size, the expectation is an exception.
    """
    _post_player(client, game_id=5)
    response = _put_game(client, game_id=5, size=12)
    _assert_error_response(response, user_message="The combination of arguments in this request is not supported.",
                           key="INVALID_ARGUMENTS", status=400)
    _wait_for(client, "SHIFT", game_id=5)


def test_post_move(client):
    """ Tests POST for /api/games/0/move

    with correct request body.
    The single player is placed on the top left corner. After pushing the leftover
    such that a move to the card to the right is possible, a move action is performed.
    It is exploited that every card has a "N" out_path.
    Expects a 200 OK, with empty body.
    State respects new position of player.
    """
    response = _post_player(client)
    player_id = _assert_ok_retrieve_id(response)
    _wait_for(client, "SHIFT")
    _post_shift(client, player_id, 0, 1, 270)
    _wait_for(client, "MOVE")
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
    _wait_for(client, "SHIFT")


def test_post_move_unreachable_move(client):
    """ Tests POST for /api/games/0/move

    with an unreachable location. The state is constructed by
    shifting the pieces next to the top left corner so that
    all outgoing paths are blocked.
    It is exploited that no card has a "W" out_path.
    Expects a 400 Bad Request, with exception body.
    State is unchanged.
    """
    response = _post_player(client)
    player_id = _assert_ok_retrieve_id(response)
    _wait_for(client, "SHIFT")
    _post_shift(client, player_id, 0, 1, 0)
    _wait_for(client, "MOVE")
    _post_move(client, player_id, 0, 0)
    _wait_for(client, "SHIFT")
    _post_shift(client, player_id, 1, 0, 90)
    _wait_for(client, "MOVE")
    response = _post_move(client, player_id, 0, 1)
    _assert_error_response(response, user_message="The sent action is invalid.",
                           key="INVALID_ACTION", status=400)


def test_post_shift_violates_turn(client):
    """ Tests POST for /api/games/0/move

    with an unreachable location. The state is constructed by
    shifting the pieces next to the top left corner so that
    all outgoing paths are blocked.
    It is exploited that no card has a "W" out_path.
    Expects a 400 Bad Request, with exception body.
    State is unchanged.
    """
    response = _post_player(client)
    player_id = _assert_ok_retrieve_id(response)
    response = _post_shift(client, player_id, 0, 1, 0)
    _assert_error_response(response, key="TURN_VIOLATION", status=400)
    _wait_for(client, "SHIFT")


def test_post_move_nonexisting_game(client):
    """ Tests POST for /api/games/1/move

    for non-existing game and with invalid location.
    Expects 404 Not Found with exception body about not found game
    """
    response = _post_player(client)
    player_id = _assert_ok_retrieve_id(response)
    data = json.dumps({
        "location": {
            "row": 7,
            "column": 0
        }
    })
    response = client.post("/api/games/8/move?p_id={}".format(player_id), data=data)
    _assert_error_response(response, user_message="The game does not exist.",
                           key="GAME_NOT_FOUND", status=404)
    _wait_for(client, "SHIFT")


def test_post_shift(client):
    """ Tests POST for /api/games/0/shift

    with correct request body.
    Expects a 200 OK, with empty body.
    State is correct about pushed in card with rotation.
    """
    response = _post_player(client)
    player_id = _assert_ok_retrieve_id(response)
    old_state = _get_state(client).get_json()
    old_leftover_card = next((card for card in old_state["maze"]["mazeCards"] if card["location"] is None),
                             None)
    old_rotation = old_leftover_card["rotation"]
    new_rotation = (old_rotation + 180) % 360
    _wait_for(client, "SHIFT")
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
    _wait_for(client, "MOVE")


def test_post_shift_with_invalid_rotation(client):
    """ Tests POST for /api/games/0/shift

    with invalid rotation.
    Expects a 400 Bad Request, with exception body.
    State is unchanged.
    """
    response = _post_player(client)
    player_id = _assert_ok_retrieve_id(response)
    _wait_for(client, "SHIFT")
    _assert_invalid_argument_and_unchanged_state(client, lambda: _post_shift(client, player_id, 0, 1, 66))


def test_post_shift_with_invalid_location(client):
    """ Tests POST for /api/games/0/shift

    with invalid rotation.
    Expects a 400 Bad Request, with exception body.
    State is unchanged.
    """
    response = _post_player(client)
    player_id = _assert_ok_retrieve_id(response)
    _wait_for(client, "SHIFT")
    _assert_invalid_action_and_unchanged_state(client, lambda: _post_shift(client, player_id, 0, 0, 90))


def test_turn_action_progression(client):
    """ Tests GET for /api/games/0/state

    expects the nextAction to change as correct actions are performed.
    """
    player_id_0 = _assert_ok_retrieve_id(_post_player(client))
    state = _get_state(client).get_json()
    assert state["nextAction"]["playerId"] == player_id_0
    assert state["nextAction"]["action"] == "PREPARE_SHIFT"
    player_id_1 = _assert_ok_retrieve_id(_post_player(client))
    state = _get_state(client).get_json()
    assert state["nextAction"]["playerId"] == player_id_0
    assert state["nextAction"]["action"] == "PREPARE_SHIFT"
    _wait_for(client, "SHIFT")
    _post_shift(client, player_id_0, 0, 1, 270)
    state = _get_state(client).get_json()
    assert state["nextAction"]["playerId"] == player_id_0
    assert state["nextAction"]["action"] == "PREPARE_MOVE"
    _wait_for(client, "MOVE")
    _post_move(client, player_id_0, 0, 0)
    state = _get_state(client).get_json()
    assert state["nextAction"]["playerId"] == player_id_1
    assert state["nextAction"]["action"] == "PREPARE_SHIFT"
    _wait_for(client, "SHIFT")
    _post_shift(client, player_id_1, 0, 1, 270)
    state = _get_state(client).get_json()
    assert state["nextAction"]["playerId"] == player_id_1
    assert state["nextAction"]["action"] == "PREPARE_MOVE"
    _wait_for(client, "MOVE")
    _post_move(client, player_id_1, 0, 6)
    state = _get_state(client).get_json()
    assert state["nextAction"]["playerId"] == player_id_0
    assert state["nextAction"]["action"] == "PREPARE_SHIFT"
    _wait_for(client, "SHIFT")


def test_no_pushback_rule(client):
    """ Tests POST for /api/games/0/shift

    expects the second shift, which tries to revert the previous shift, to fail
    """
    player_id_0 = _assert_ok_retrieve_id(_post_player(client))
    player_id_1 = _assert_ok_retrieve_id(_post_player(client))
    _wait_for(client, "SHIFT")
    _post_shift(client, player_id_0, 0, 1, 270)
    _wait_for(client, "MOVE")
    _post_move(client, player_id_0, 0, 0)
    _wait_for(client, "SHIFT")
    _assert_invalid_action_and_unchanged_state(client, lambda: _post_shift(client, player_id_1, 6, 1, 270))


def test_get_computation_methods_contains_library(library_path, client):
    """ Tests GET for /api/computation-methods

    The returned methods should contain the library.
    """
    expected_name, ext = os.path.splitext(os.path.basename(library_path))
    computation_methods = _get_computation_methods(client).get_json()
    assert expected_name in computation_methods


def test_remove_overdue_players__with_two_overdue_players__should_remove_player(client, cli_runner):
    """ Tests the cli to remove overdue players.

    Sets the overdue time to 1s and waits 2s before executing cli."""
    player_id_1 = _assert_ok_retrieve_id(_post_player(client))
    player_id_2 = _assert_ok_retrieve_id(_post_player(client))
    _wait_for(client, "SHIFT")
    _post_shift(client, player_id_1, 0, 1, 270)
    time.sleep(2)

    _cli_remove_overdue_players(cli_runner, 1)

    state = _get_state(client).get_json()
    assert len(state["players"]) == 1
    assert state["players"][0]["id"] == player_id_2


def test_remove_overdue_players__with_one_overdue_player__should_remove_player(client, cli_runner):
    """ Tests the cli to remove overdue players.

    A single player is not removed. When a second player joins, the countdown starts for the first player.
    Sets the overdue time to 1s and waits 2s before executing cli."""
    player_id_1 = _assert_ok_retrieve_id(_post_player(client))
    _wait_for(client, "SHIFT")
    _post_shift(client, player_id_1, 0, 1, 270)
    time.sleep(2)
    _cli_remove_overdue_players(cli_runner, 1)
    state = _get_state(client).get_json()
    assert len(state["players"]) == 0


def test_remove_unobserved_games__with_one_unobserved_game__should_remove_game(client, cli_runner):
    """ Tests the cli to remove unobserved games.

    Sets the max unobserved time to 1s and waits 2s before executing cli.
    The initial observed timestamp will be set with the first GET state.
    Only the updates to this timestamp are delayed."""
    _post_player(client, game_id=7)
    response = _get_state(client, game_id=7)
    assert response.status_code == 200
    time.sleep(2)
    _cli_remove_unobserved_games(cli_runner, 1)
    response = _get_state(client, game_id=7)
    _assert_error_response(response, key="GAME_NOT_FOUND", status=404)


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


def _assert_ok_retrieve_id(post_player_response):
    """ Asserts that a response has a 200 OK status,
    and returns the identifier of the added player
    """
    assert post_player_response.status_code == 200
    try:
        return int(post_player_response.get_json()["id"])
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
    assert message["key"] == key
    if user_message:
        assert message["userMessage"] == user_message
    if user_message_contains:
        assert user_message_contains in message["userMessage"]


def _wait_for(client, expected_action, timeout=timedelta(seconds=3), game_id=0):
    """ Retrieves game state until expected action is required """
    poll_frequency = timedelta(milliseconds=600)
    state = _get_state(client, game_id=game_id).get_json()
    start = time.time()
    while state["nextAction"]["action"] != expected_action and (time.time() - start < timeout.total_seconds()):
        time.sleep(poll_frequency.total_seconds())
        state = _get_state(client, game_id=game_id).get_json()
    assert state["nextAction"]["action"] == expected_action


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


def _post_player(client, is_bot=False, computation_method=None, game_id=0, name=None):
    player_data = _player_data(is_bot, computation_method, name)
    return client.post("/api/games/{}/players".format(game_id), data=player_data, mimetype="application/json")


def _delete_player(client, player_id):
    return client.delete("/api/games/0/players/{}".format(player_id))


def _put_player_name(client, player_id, name, game_id=0):
    name_data = json.dumps({"name": name})
    return client.put(f"/api/games/{game_id}/players/{player_id}/name", data=name_data, mimetype="application/json")


def _put_game(client, game_id=0, size=7):
    game_data = json.dumps({"mazeSize": size}) if size else None
    return client.put(f"/api/games/{game_id}", data=game_data, mimetype="application/json")


def _get_state(client, game_id=0):
    return client.get(f"/api/games/{game_id}/state")


def _get_computation_methods(client):
    return client.get("/api/computation-methods")


def _get_generate_board(client, size=None):
    param = "?size="+str(size) if size else ""
    return client.get("/api/random-board"+param)


def _player_data(is_bot=False, computation_method=None, name=None):
    data = {}
    if is_bot:
        data = {
            "isBot": is_bot,
            "computationMethod": computation_method
        }
    if name:
        data["name"] = name
    return json.dumps(data) if len(data) else None


def _cli_remove_overdue_players(cli_runner, seconds):
    cli_runner.invoke(args=["game-management", "remove-overdue-players", "--seconds", str(seconds)])


def _cli_remove_unobserved_games(cli_runner, seconds):
    cli_runner.invoke(args=["game-management", "remove-unobserved-games", "--seconds", str(seconds)])
