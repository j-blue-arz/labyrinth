""" This module deals with input validation of players' actions,
if these cannot be validated with the basic model methods.

Currently it only has one class to validate a user's move in the labyrinth.
"""
from collections import deque


class MoveValidator():
    """ Validates if a move is valid.

    Performs a BFS in a graph represented by the current maze to
    verify if two locations are connected.
    """

    def __init__(self, maze):
        self._maze = maze

    def validate_move(self, source_location, target_location):
        """ Validates if a move is valid.

        Performs a BFS in a graph represented by the current maze to
        verify if the source location and the target location
        are connected.

        :param source_location: the current BoardLocation
        :param target_location: the requested BoardLocation
        :return: True, iff there is a path between the two locations
        """
        reachable_locations = self._bfs(source_location)
        return target_location in reachable_locations

    def _bfs(self, source):
        """ Performs a BFS, returning all reachable BoardLocations

        :param source: the BoardLocation to start from
        :return: a set of reachable BoardLocations
        """
        reached = set([source])
        next_elements = deque([source])
        while next_elements:
            current = next_elements.popleft()
            for neighbor in self._neighbors(current):
                if neighbor not in reached:
                    reached.add(neighbor)
                    next_elements.append(neighbor)
        return reached

    def _neighbors(self, location):
        """ Returns an iterator over valid neighbors
        of the given BoardLocation, with the current state of the maze """
        def _mirror(delta_tuple):
            return (-delta_tuple[0], -delta_tuple[1])
        maze_card = self._maze[location]
        for delta in maze_card.out_paths():
            location_to_test = location.add(*delta)
            if self._maze.is_inside(location_to_test):
                card_to_test = self._maze[location_to_test]
                if card_to_test.has_out_path(_mirror(delta)):
                    yield location_to_test
