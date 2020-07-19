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


def param_tuple_to_param_dict(maze_string, leftover_out_paths, piece_starts, objective):
    """ Converts a tuple of board state defining parameters to a dictionary,
    which can be used by create_board_and_pieces.

    :param maze_string: a string defining a maze
    :param leftover_out_paths: the out paths of the leftover maze card
    :param piece_starts: a list of starting locations of pieces on the board. The number of pieces will be equal to
    the size of this list. Each location is a 2-tuple.
    :param objective: the location (2-tuple) of the objective,
    or 'leftover' to denote that the objective is the leftover maze card
    """
    maze_card_factory = MazeCardFactory()
    maze = create_maze(maze_string, maze_card_factory)
    leftover_card = maze_card_factory.create_instance(leftover_out_paths, 0)
    param_dict = {"maze": maze,
                  "leftover_card": leftover_card,
                  "piece_locations": [BoardLocation(*piece_start) for piece_start in piece_starts]}
    if type(objective) == tuple:
        param_dict["objective_location"] = BoardLocation(*objective)
    elif objective == "leftover":
        param_dict["objective_maze_card"] = leftover_card
    return param_dict


def create_board_and_pieces(maze, leftover_card, piece_locations, objective_location=None, objective_maze_card=None):
    maze = copy.deepcopy(maze)
    if not objective_maze_card:
        objective_maze_card = maze[objective_location]
    board = Board(maze=maze, leftover_card=leftover_card, objective_maze_card=objective_maze_card)
    board.clear_pieces()
    for index, location in enumerate(piece_locations):
        piece = Piece(index, board.maze[location])
        board.pieces.append(piece)
    return board
