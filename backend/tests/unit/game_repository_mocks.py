from unittest.mock import Mock

from labyrinth.model import interactors


def when_game_repository_find_by_id_then_return(game):
    game_repository_mock = Mock(spec=interactors.GameRepository)
    game_id = game.identifier

    def return_game(requested_game_id):
        if requested_game_id == game_id:
            return game
        else:
            return None

    game_repository_mock.find_by_id = Mock(side_effect=return_game)
    return game_repository_mock
