""" Provides random board and maze generation.

In contrast to the factories in server.model.factories, this module has almost no guarantees on the layout
of the created mazes and on the ratio of placed maze cards."""
import random
from server.model.game import MazeCard, Maze, BoardLocation
from server.model.factories import MazeCardFactory

def create_random_maze(maze_card_factory=None):
    """ Generates a random maze state.
    Corners of the maze are fixed as corners
    """
    fixed_cards = {
        BoardLocation(0, 0): MazeCard(doors=MazeCard.CORNER, rotation=90),
        BoardLocation(0, 6): MazeCard(doors=MazeCard.CORNER, rotation=180),
        BoardLocation(6, 6): MazeCard(doors=MazeCard.CORNER, rotation=270),
        BoardLocation(6, 0): MazeCard(doors=MazeCard.CORNER, rotation=0)}

    if not maze_card_factory:
        maze_card_factory = MazeCardFactory()
    maze = Maze()

    def card_at(location):
        if location in fixed_cards:
            return maze_card_factory.create_instance(fixed_cards[location].doors, fixed_cards[location].rotation)
        return maze_card_factory.create_random_maze_card()

    for location in maze.maze_locations:
        maze[location] = card_at(location)
    return maze