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
    verify if two locations are connected, or to determine all reachable locations
    from one or more sources.
    """
    def __init__(self, maze):
        self._maze = maze
        self._reached_locations = {}

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
        """ Performs a BFS, returning all reachable BoardLocations.
        Either source or sources has to be provided

        :param source: a BoardLocations to start from.
        :param sources: an iterable of BoardLocations.
        :param with_sources: if True, includes the sources of the reached board locations.
                             Only possible if multiple sources are given.
        :return: a set of BoardLocations, or ReachedLocations if with_sources was set to True
        """
        if sources is None:
            return self._single_source_bfs(source)
        else:
            return self._multi_source_bfs(sources, with_sources)

    def _multi_source_bfs(self, sources, with_sources=False):
        reached_locations = {ReachedLocation(source, source) for source in sources}
        self._reached_locations = set(sources)
        next_elements = deque(reached_locations)
        while next_elements:
            current = next_elements.popleft()
            for neighbor in self._neighbors(current.location):
                reached_location = ReachedLocation(neighbor, current.source)
                if reached_location not in reached_locations:
                    reached_locations.add(reached_location)
                    self._reached_locations.add(neighbor)
                    next_elements.append(reached_location)
        if not with_sources:
            return {reached.location for reached in reached_locations}
        return reached_locations

    def _single_source_bfs(self, source):
        self._reached_locations = {source}
        next_elements = deque([source])
        while next_elements:
            current = next_elements.popleft()
            for neighbor in self._neighbors(current):
                if neighbor not in self._reached_locations:
                    self._reached_locations.add(neighbor)
                    next_elements.append(neighbor)
        return self._reached_locations


    def _neighbors(self, location):
        """ Returns an iterator over valid neighbor BoardLocations
        of the given BoardLocation, with the current state of the maze """
        def _mirror(delta_tuple):
            return (-delta_tuple[0], -delta_tuple[1])
        maze_card = self._maze[location]
        for delta in maze_card.out_paths():
            location_to_test = location.add(*delta)
            if location_to_test not in self._reached_locations:
                if self._maze.is_inside(location_to_test):
                    card_to_test = self._maze[location_to_test]
                    if card_to_test.has_out_path(_mirror(delta)):
                        yield location_to_test

def _generate_out_path_dict():
    _direction_to_door = {(-1, 0): "N", (0, 1): "E", (1, 0): "S", (0, -1): "W"}

    def _has_out_path(direction, rotation, doors):
        door = _direction_to_door[direction]
        door_index = "NESW".find(door)
        turns = (rotation // 90)
        adapted_index = (door_index - turns + 4) % 4
        adapted_door = "NESW"[adapted_index]
        return adapted_door in doors

    def _out_paths(doors, rotation):
        for direction in _direction_to_door:
            if _has_out_path(direction, rotation, doors):
                yield direction

    out_path_dict = dict()
    for doors in ["NS", "NE", "NES"]:
        for rotation in [0, 90, 180, 270]:
            out_paths = _out_paths(doors, rotation)
            out_path_dict[(doors, rotation)] = set(out_paths)
    return out_path_dict

class RotatableMazeCardGraph:
    """ Performs BFS on a graph represented by a maze.
    Allows for a specific maze card to be rotatable. """

    _OUT_PATH_DICT = _generate_out_path_dict()

    def __init__(self, maze, rotatable_maze_card_location):
        self._maze = maze
        self._certainly_reached = {}
        self._rotatable = rotatable_maze_card_location
        self._rotatable_touched_directions = []
        self._rotation_map = dict()

    def reachable_locations(self, source):
        """ Performs a BFS, returning all reachable BoardLocations.
        The maze card at the given rotatable location is considered for all its rotations.

        :param source: a BoardLocations to start from.
        :return: a set s of reachable locations, and a map m of the form {r: locations}.
                 The locations in s are reachable in any case.
                 The locations in m are reachable if the rotatable card has rotation r.
                 the rotatable card itself is never contained in s.
                 If a certain key is not present in the dictionary, the rotatable is not reachable for this rotation.
        """
        # The algorithm runs in two phases.
        # First phase performs standard bfs, and keeps track of all directions from which the rotatable
        #        could have been reached (= touched)
        # Second phase tries all rotations, checks if the rotatable is reached, and performs a bfs without touching
        #        already reached cards
        self._certainly_reached = self._determine_reachable(source, self._rotatable)
        self._determine_rotation_dependend_reachable()
        return self._certainly_reached, self._rotation_map

    def _determine_reachable(self, source, rotatable):
        reached = {}
        if source == rotatable:
            self._rotatable_touched_directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]
            reached = {}
        else:
            reached = {source}
            next_elements = deque([source])
            while next_elements:
                current = next_elements.popleft()
                for neighbor in self._reachable_neighbors(current, rotatable):
                    if neighbor not in reached and neighbor not in self._certainly_reached:
                        reached.add(neighbor)
                        next_elements.append(neighbor)
        return reached

    def _determine_rotation_dependend_reachable(self):
        if self._rotatable_touched_directions:
            rotatable_card = self._maze[self._rotatable]
            original_rotation = rotatable_card.rotation
            for rotation in self._rotations(rotatable_card):
                rotatable_card.rotation = rotation
                entered_paths = list(filter(rotatable_card.has_out_path, self._rotatable_touched_directions))
                if entered_paths:
                    self._rotation_map[rotation] = self._determine_reachable(self._rotatable, None)
            rotatable_card.rotation = original_rotation


    def _reachable_neighbors(self, location, rotatable):
        """ Returns an iterator over valid neighbor BoardLocations
        of the given BoardLocation, with the current state of the maze """
        def _mirror(delta_tuple):
            return (-delta_tuple[0], -delta_tuple[1])
        maze_card = self._maze[location]
        for delta in maze_card.out_paths():
            location_to_test = location.add(*delta)
            if location_to_test == rotatable:
                self._rotatable_touched_directions.append(_mirror(delta))
            elif self._maze.is_inside(location_to_test):
                card_to_test = self._maze[location_to_test]
                if card_to_test.has_out_path(_mirror(delta)):
                    yield location_to_test

    def _rotations(self, maze_card):
        rotations = [0, 90, 180, 270]
        if maze_card.doors == maze_card.STRAIGHT:
            rotations = [0, 90]
        return rotations
