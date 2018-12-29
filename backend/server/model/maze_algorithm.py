""" This module deals with graph algorithms performed on the maze,

Currently it only has one class to compute all reachable locations.
"""
from collections import deque

class ReachedLocation:
    """ A container type for a location reached in the search from the source """
    def __init__(self, location, source):
        self._location = location
        self._source = source

    @property
    def location(self):
        """ Getter for location """
        return self._location

    @property
    def source(self):
        """ Getter for source """
        return self._source

    def __eq__(self, other):
        return isinstance(self, type(other)) and \
            self._location == other._location

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self._location)

    def __str__(self):
        return "{} -> {}".format(self._source, self._location)

    def __repr__(self):
        return self.__str__()

class Graph:
    """ Performs a BFS in a graph represented by the current maze to
    verify if two locations are connected.
    """

    def __init__(self, maze):
        self._maze = maze

    def is_reachable(self, source_location, target_location):
        """ Performs a BFS in a graph represented by the current maze to
        verify if the source location and the target location
        are connected.

        :param source_location: the current BoardLocation
        :param target_location: the requested BoardLocation
        :return: True, iff there is a path between the two locations
        """
        reachable_locations = self.reachable_locations(source_location)
        return target_location in reachable_locations

    def reachable_locations(self, source=None, sources=None, with_sources=False):
        """ Performs a multi-source BFS, returning all reachable BoardLocations.
        Either source or sources has to be provided

        :param source: a BoardLocations to start from.
        :param sources: an iterable of BoardLocations.
        :param with_sources: if True, includes the sources of the reached board locations
        :return: a set of BoardLocations, or ReachedLocations if with_sources was set to True
        """
        if sources is None:
            sources = [source]
        reached_locations = {ReachedLocation(source, source) for source in sources}
        next_elements = deque(reached_locations)
        while next_elements:
            current = next_elements.popleft()
            for neighbor in self._neighbors(current.location):
                reached_location = ReachedLocation(neighbor, current.source)
                if reached_location not in reached_locations:
                    reached_locations.add(reached_location)
                    next_elements.append(reached_location)
        if not with_sources:
            return {reached.location for reached in reached_locations}
        return reached_locations

    def _neighbors(self, location):
        """ Returns an iterator over valid neighbor BoardLocations
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
