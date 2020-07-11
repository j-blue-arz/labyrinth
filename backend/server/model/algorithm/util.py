""" This module contains utility functions for the algorithms implemented in this package.
"""
import server.model.game as game

def other(player):
    """ Returns the identifier of the respective other player in a two player game,
    if the two identifiers are 0 and 1 """
    return 1 - player

def sign(player):
    """ Returns the sign of a player in a two-player minimax algorithm.
    Player 0 is the maximizing, player 1 the minimizing player."""
    return 1 - 2*player


def copy_board(board, pieces=None):
    """ Copies the state of a game. This method should be used instead of copy.deepcopy() for better performance """
    maze_card_by_id = {}
    existing_leftover = board.leftover_card
    leftover_card = game.MazeCard(existing_leftover.identifier, existing_leftover.out_paths, existing_leftover.rotation)
    maze_card_by_id[leftover_card.identifier] = leftover_card
    maze = game.Maze(validate_locations=False, maze_size=board.maze.maze_size)
    for location in board.maze.maze_locations:
        old_maze_card = board.maze[location]
        maze_card = game.MazeCard(old_maze_card.identifier, old_maze_card.out_paths, old_maze_card.rotation)
        maze_card_by_id[maze_card.identifier] = maze_card
        maze[location] = maze_card
    objective = maze_card_by_id[board.objective_maze_card.identifier]
    board_copy = game.Board(maze, leftover_card, objective)
    board_copy.validate_moves = False
    if not pieces:
        pieces = board.pieces
    piece_maze_cards = [maze_card_by_id[piece.maze_card.identifier] for piece in pieces]
    for index, maze_card in enumerate(piece_maze_cards):
        board_copy.pieces.append(game.Piece(index, maze_card))
    return board_copy

def find_location_by_id(maze, card_id):
    for location in maze.maze_locations:
        if maze[location].identifier == card_id:
            return location
    return None


def generate_rotated_out_path_dict():
    _out_path_by_direction = {(-1, 0): "N", (0, 1): "E", (1, 0): "S", (0, -1): "W"}

    def _has_out_path(direction, rotation, out_paths):
        out_path = _out_path_by_direction[direction]
        out_path_index = "NESW".find(out_path)
        turns = (rotation // 90)
        rotation_aware_index = (out_path_index - turns + 4) % 4
        rotated_out_path = "NESW"[rotation_aware_index]
        return rotated_out_path in out_paths

    def _rotated_directions(out_paths, rotation):
        for direction in _out_path_by_direction:
            if _has_out_path(direction, rotation, out_paths):
                yield direction

    out_path_dict = dict()
    for out_paths in ["NS", "NE", "NES", "NESW"]:
        for rotation in [0, 90, 180, 270]:
            rotated_directions = _rotated_directions(out_paths, rotation)
            out_path_dict[(out_paths, rotation)] = set(rotated_directions)
    return out_path_dict
