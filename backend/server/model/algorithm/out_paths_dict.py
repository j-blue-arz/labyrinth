""" This module contains a dictionary to speed up the computation of rotated out_paths.

The dictionary maps tuples of (out_paths, rotation) to a set of directions.
out_paths is a string over 'NESW', a direction is a tuple (x-direction, y-direction).

The module implements a singleton pattern.
The dictionary is created when the module is imported for the first time.
"""


def _generate_rotated_out_path_dict():
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


dictionary = _generate_rotated_out_path_dict()
