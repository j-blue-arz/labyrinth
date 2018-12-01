""" Tests mapper module:
tests the mapping from a Game instance to the DTO by
creating a Game instance by hand, mapping it to DTO,
mapping the DTO back to a Game and then asserting the structure of the result """
import server.mapper as mapper
from domain.model import Game, MazeCard, BoardLocation


def _create_test_game():
    """ Creates a Game instance by hand """
    game = Game()
    player_ids = [game.add_player(), game.add_player()]
    game.leftover_card = MazeCard(0, MazeCard.T_JUNCT, 0)
    card_id = 1
    for row in range(game.board.BOARD_SIZE):
        for column in range(game.board.BOARD_SIZE):
            if row == 0 and column == 0:
                game.board[BoardLocation(row, column)] = MazeCard(card_id, MazeCard.STRAIGHT, 0)
            elif row == 1 and column == 1:
                game.board[BoardLocation(row, column)] = MazeCard(card_id, MazeCard.CORNER, 0)
            elif row == 2 and column == 2:
                game.board[BoardLocation(row, column)] = MazeCard(card_id, MazeCard.T_JUNCT, 270)
            else:
                game.board[BoardLocation(row, column)] = MazeCard(card_id, MazeCard.T_JUNCT, 0)
    game.find_player(player_ids[0]).maze_card = game.board[BoardLocation(3, 3)]
    game.find_player(player_ids[1]).maze_card = game.board[BoardLocation(5, 5)]
    return game, player_ids


def test_mapping_for_player():
    """ Tests correct mapping of player """
    created_game, player_ids = _create_test_game()
    game_dto = mapper.game_to_dto(created_game)
    game = mapper.dto_to_game(game_dto)
    assert len(game.players) == 2
    assert game.find_player(player_ids[0])
    assert game.find_player(player_ids[1])
    assert _compare_games_using_function(created_game, game,
                                         lambda g: g.find_player(player_ids[0]).maze_card.identifier)
    assert _compare_games_using_function(created_game, game,
                                         lambda g: g.find_player(player_ids[1]).maze_card.identifier)


def test_mapping_for_leftover():
    """ Tests correct mapping of leftover maze card """
    created_game, _ = _create_test_game()
    game_dto = mapper.game_to_dto(created_game)
    game = mapper.dto_to_game(game_dto)
    assert _compare_maze_cards(*map(lambda g: g.leftover_card, [created_game, game]))


def test_mapping_for_board():
    """ Tests correct mapping of current board state """
    created_game, _ = _create_test_game()
    game_dto = mapper.game_to_dto(created_game)
    game = mapper.dto_to_game(game_dto)
    for location in game.board.board_locations():
        assert _compare_maze_cards(*map(lambda g: g.board[location], [created_game, game]))
    assert _compare_maze_cards(*map(lambda g: g.leftover_card, [created_game, game]))


def _compare_maze_cards(maze_card1, maze_card2):
    """ Compares identifier, doors and rotation of MazeCard instances """
    return maze_card1.identifier == maze_card2.identifier and \
        maze_card1.doors == maze_card2.doors and \
        maze_card1.rotation == maze_card2.rotation


def _compare_games_using_function(game1, game2, func):
    """ compares two instances of Game using a function, i.e.
    determines if func(game1) == func(game2)
    """
    return func(game1) == func(game2)
