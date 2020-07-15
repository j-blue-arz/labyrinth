""" Provides random board and maze generation.

In contrast to the factories in app.model.factories, this module has almost no guarantees on the layout
of the created mazes and on the ratio of placed maze cards."""
import copy
from app.model.game import MazeCard, Maze, BoardLocation, Board, Piece
from app.model.factories import create_maze, MazeCardFactory


def create_random_maze(maze_card_factory=None):
    """ Generates a random maze state.
    Corners of the maze are fixed as corners
    """
    fixed_cards = {
        BoardLocation(0, 0): MazeCard(out_paths=MazeCard.CORNER, rotation=90),
        BoardLocation(0, 6): MazeCard(out_paths=MazeCard.CORNER, rotation=180),
        BoardLocation(6, 6): MazeCard(out_paths=MazeCard.CORNER, rotation=270),
        BoardLocation(6, 0): MazeCard(out_paths=MazeCard.CORNER, rotation=0)}

    if not maze_card_factory:
        maze_card_factory = MazeCardFactory()
    maze = Maze()

    def card_at(location):
        if location in fixed_cards:
            return maze_card_factory.create_instance(fixed_cards[location].out_paths, fixed_cards[location].rotation)
        return maze_card_factory.create_random_maze_card()

    for location in maze.maze_locations:
        maze[location] = card_at(location)
    return maze


def param_tuple_to_param_dict(maze_string, leftover_out_paths, piece_starts, objective_tuple):
    maze_card_factory = MazeCardFactory()
    return {"maze": create_maze(maze_string, maze_card_factory),
            "leftover_card": maze_card_factory.create_instance(leftover_out_paths, 0),
            "piece_locations": [BoardLocation(*piece_start) for piece_start in piece_starts],
            "objective_location": BoardLocation(*objective_tuple)}


def create_board_and_pieces(maze, leftover_card, piece_locations, objective_location):
    maze = copy.deepcopy(maze)
    board = Board(maze=maze, leftover_card=leftover_card, objective_maze_card=maze[objective_location])
    board.clear_pieces()
    for index, location in enumerate(piece_locations):
        piece = Piece(index, board.maze[location])
        board.pieces.append(piece)
    return board
