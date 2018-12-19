""" Tests mapper module.
Tests the main methods dto_to_game() and game_to_dto(), i.e.
the methods used to persist a Game instance.
The tests are performed by creating a Game instance by hand, mapping it to DTO,
mapping the DTO back to a Game and then asserting the structure of the result """
import server.mapper.persistence as mapper
from server.model.game import Game, MazeCard, BoardLocation, Turns, Player, PlayerAction, Board
from server.model.computer import ComputerPlayer, RandomActionsAlgorithm


def _create_test_game(with_computer=False):
    """ Creates a Game instance by hand """
    board = Board(leftover_card=MazeCard(0, MazeCard.T_JUNCT, 0))
    for row in range(board.maze.MAZE_SIZE):
        for column in range(board.maze.MAZE_SIZE):
            if row == 0 and column == 0:
                board.maze[BoardLocation(row, column)] = MazeCard.create_instance(MazeCard.STRAIGHT, 0)
            elif row == 1 and column == 1:
                board.maze[BoardLocation(row, column)] = MazeCard.create_instance(MazeCard.CORNER, 0)
            elif row == 2 and column == 2:
                board.maze[BoardLocation(row, column)] = MazeCard.create_instance(MazeCard.T_JUNCT, 270)
            else:
                board.maze[BoardLocation(row, column)] = MazeCard.create_instance(MazeCard.T_JUNCT, 0)
    player_ids = [3, 4]
    players = [Player(identifier=player_id, game_identifier=7) for player_id in player_ids]
    if with_computer:
        player_ids.append(42)
        players.append(ComputerPlayer(identifier=42, game_identifier=7,
                                      algorithm_name="random", shift_url="shift-url", move_url="move-url"))
    for player in players:
        player.set_board(board)
    players[0].piece.maze_card = board.maze[BoardLocation(3, 3)]
    players[1].piece.maze_card = board.maze[BoardLocation(5, 5)]
    board._objective_maze_card = board.maze[BoardLocation(1, 4)]
    turns = Turns(players, next_action=PlayerAction(players[1], PlayerAction.MOVE_ACTION))
    game = Game(identifier=7, turns=turns, board=board, players=players)
    return game, player_ids


def test_mapping_for_player():
    """ Tests correct mapping of player """
    created_game, player_ids = _create_test_game()
    game_dto = mapper.game_to_dto(created_game)
    game = mapper.dto_to_game(game_dto)
    assert game.get_player(player_ids[0]).identifier == player_ids[0]
    assert game.get_player(player_ids[1]).identifier == player_ids[1]
    assert _compare_games_using_function(created_game, game,
                                         lambda g: g.get_player(player_ids[0]).piece.maze_card.identifier)
    assert _compare_games_using_function(created_game, game,
                                         lambda g: g.get_player(player_ids[1]).piece.maze_card.identifier)


def test_mapping_for_computer_player():
    """ Tests correct mapping for computer player """
    created_game, player_ids = _create_test_game(with_computer=True)
    game_dto = mapper.game_to_dto(created_game)
    game = mapper.dto_to_game(game_dto)
    computer_player = game.get_player(player_ids[2])
    assert isinstance(computer_player, ComputerPlayer)
    assert computer_player.algorithm == RandomActionsAlgorithm
    assert computer_player.shift_url == "shift-url"
    assert computer_player.move_url == "move-url"


def test_mapping_for_leftover():
    """ Tests correct mapping of leftover maze card """
    created_game, _ = _create_test_game()
    game_dto = mapper.game_to_dto(created_game)
    game = mapper.dto_to_game(game_dto)
    assert _compare_maze_cards(*map(lambda g: g.board.leftover_card, [created_game, game]))


def test_mapping_for_maze():
    """ Tests correct mapping of current maze state """
    created_game, _ = _create_test_game()
    game_dto = mapper.game_to_dto(created_game)
    game = mapper.dto_to_game(game_dto)
    for location in game.board.maze.maze_locations():
        assert _compare_maze_cards(*map(lambda g: g.board.maze[location], [created_game, game]))
    assert _compare_maze_cards(*map(lambda g: g.board.leftover_card, [created_game, game]))


def test_mapping_for_objectives():
    """ Tests correct mapping of players' objective """
    created_game, player_ids = _create_test_game()
    game_dto = mapper.game_to_dto(created_game)
    game = mapper.dto_to_game(game_dto)
    assert _compare_games_using_function(created_game, game,
                                         lambda g: g.board.objective_maze_card.identifier)


def test_mapping_turns():
    """ Tests correct mapping of next actions """
    created_game, player_ids = _create_test_game()
    game_dto = mapper.game_to_dto(created_game)
    game = mapper.dto_to_game(game_dto)
    for _ in range(len(player_ids) * 2):
        _compare_games_using_function(created_game, game,
                                      lambda g: g.turns.next_player_action().player)
        _compare_games_using_function(created_game, game,
                                      lambda g: g.turns.next_player_action().action)
        game.turns.perform_action(game.turns.next_player_action().player, game.turns.next_player_action().action)
        created_game.turns.perform_action(created_game.turns.next_player_action().player,
                                          created_game.turns.next_player_action().action)


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
