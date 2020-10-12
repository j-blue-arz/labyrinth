import json
import os

from labyrinth.model.game import BoardLocation
import tests.unit.factories as setup


def deserialize_instance_json(filename):
    instance = None
    with open(filename, mode="r") as infile:
        instance = json.load(infile)
    maze_string = "\n".join([""] + instance["maze_array"])

    leftover_out_paths = instance["leftover"]
    piece_locations = [(json_loc["row"], json_loc["column"]) for json_loc in instance["piece_locations"]]
    objective_location = (instance["objective"]["row"], instance["objective"]["column"])
    if objective_location == (-1, -1):
        objective_location = "leftover"
    param_dict = setup.param_tuple_to_param_dict(maze_string=maze_string,
                                                 leftover_out_paths=leftover_out_paths,
                                                 piece_starts=piece_locations,
                                                 objective=objective_location)
    board = setup.create_board_and_pieces(**param_dict)
    return board, instance["name"]


def serialize_instance_json(board, outfolder, instance_name):
    filename = os.path.join(outfolder, f"{instance_name}.json")
    with open(filename, mode="w") as outfile:
        piece_locations = [board.maze.maze_card_location(piece.maze_card) for piece in board.pieces]
        piece_location_dicts = [{"row": location.row, "column": location.column} for location in piece_locations]
        objective_location = _objective_as_location_or_leftover(board)
        out_dict = {
            "name": instance_name,
            "maze_array": maze_to_string_array(board.maze),
            "leftover": board.leftover_card.out_paths,
            "piece_locations": piece_location_dicts,
            "objective": {"row": objective_location.row, "column": objective_location.column}
        }
        json.dump(out_dict, outfile, indent=4)


def serialize_instance_text(board, outfolder, instance_name):
    filename = os.path.join(outfolder, f"{instance_name}.txt")
    with open(filename, mode="w") as outfile:
        maze_size = board.maze.maze_size
        piece_locations = [board.maze.maze_card_location(piece.maze_card) for piece in board.pieces]
        objective_location = _objective_as_location_or_leftover(board)
        outfile.write(f"{instance_name}\n")
        outfile.write(f"{maze_size} {len(piece_locations)}\n")
        string_array = maze_to_string_array(board.maze)
        for line in string_array:
            outfile.write(f"{line}\n")
        outfile.write(f"{board.leftover_card.out_paths}\n")
        for location in piece_locations:
            outfile.write(f"{location.row} {location.column}\n")
        outfile.write(f"{objective_location.row} {objective_location.column}\n")


def maze_to_string_array(maze):
    """ Writes a maze as an array of strings, as defined in factories.create_maze() """
    def as_multi_line_string(maze_card):
        result = [
            ["#", "N", "#", ],
            ["W", ".", "E"],
            ["#", "S", "#"]
        ]
        path_to_symbol = {True: ".", False: "#"}
        result[0][1] = path_to_symbol[maze_card.has_rotated_out_path((-1, 0))]
        result[1][0] = path_to_symbol[maze_card.has_rotated_out_path((0, -1))]
        result[1][2] = path_to_symbol[maze_card.has_rotated_out_path((0, 1))]
        result[2][1] = path_to_symbol[maze_card.has_rotated_out_path((1, 0))]
        return list(map(lambda char_list: "".join(char_list), result))

    result = []
    for row in range(0, maze.maze_size):
        string_arrays = [as_multi_line_string(maze[BoardLocation(row, column)]) for column in range(0, maze.maze_size)]
        for line_part in zip(*string_arrays):
            line = "|".join(line_part)
            line = line + "|"
            result.append(line)
        result.append("-" * (maze.maze_size * 4 - 1) + "|")
    return result


def _objective_as_location_or_leftover(board):
    """ Determines an identifier for the objective: either its location,
    or the location (-1, -1) to denote the leftover."""
    objective_location = board.maze.maze_card_location(board.objective_maze_card)
    return objective_location or BoardLocation(-1, -1)
