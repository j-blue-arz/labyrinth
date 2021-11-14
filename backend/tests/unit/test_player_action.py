from labyrinth.model.game import Player, PlayerAction


def test_copy_with_prepare__with_prepare_action__should_return_copy():
    player = Player(2)
    player_action = PlayerAction(player, PlayerAction.PREPARE_MOVE)
    player_action_copy = player_action.copy_with_prepare()

    assert player_action_copy.player == player
    assert player_action_copy.action == PlayerAction.PREPARE_MOVE


def test_copy_with_prepare__with_shift_action__should_return_copy_with_prepare_shift():
    player = Player(2)
    player_action = PlayerAction(player, PlayerAction.SHIFT_ACTION)
    player_action_copy = player_action.copy_with_prepare()

    assert player_action_copy.player == player
    assert player_action_copy.action == PlayerAction.PREPARE_SHIFT
