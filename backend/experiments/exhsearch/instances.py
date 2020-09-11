""" Generates instances for exhaustive search algorithm. """

import json
import os

import click
from tqdm import tqdm

from experiments.exhsearch import depths as exhsearch_depths
from labyrinth.model.game import BoardLocation


@click.command()
@click.option("--outfolder", required=True)
@click.option("--library", required=True)
@click.option("--depths", "-d", "depths_by_size", nargs=2, default=[(7, 2)], type=click.Tuple((int, int)),
              required=True, multiple=True,
              help="Depths for each maze size. Specify in the form -d <maze size> <depth>. \
                  It is possible to specify the parameter multiple times.")
@click.option("--num_instances", default=10, show_default=True)
@click.option("--json/--nojson", "json", default=True)
@click.option("--text/--notext", "text", default=False,
              help="serializes instances as text. This is helpful for ecosystems without built-in json support.")
def run(depths_by_size, num_instances, outfolder, library, json, text):
    maze_sizes = {size for size, depth in depths_by_size}
    for maze_size in maze_sizes:
        depths = {depth for size, depth in depths_by_size if size == maze_size}
        print(f"generating instances for maze size {maze_size}")
        pbar = tqdm(total=len(depths)*num_instances)
        still_required = {depth: num_instances for depth in depths}
        while still_required:
            board = exhsearch_depths.generate_board(maze_size)
            depth = exhsearch_depths.determine_exhsearch_depths(board, library)
            if depth in still_required:
                if json:
                    serialize_instance_json(board, depth, still_required[depth], outfolder)
                if text:
                    serialize_instance_text(board, depth, still_required[depth], outfolder)
                still_required[depth] = still_required[depth] - 1
                pbar.update(1)
                if still_required[depth] == 0:
                    still_required.pop(depth)
        pbar.close()


def serialize_instance_json(board, depth, number, outfolder):
    maze_size = board.maze.maze_size
    instance_name = f"exhsearch_s{maze_size}_d{depth}_num{number}"
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


def serialize_instance_text(board, depth, number, outfolder):
    maze_size = board.maze.maze_size
    instance_name = f"exhsearch_s{maze_size}_d{depth}_num{number}"
    filename = os.path.join(outfolder, f"{instance_name}.txt")
    with open(filename, mode="w") as outfile:
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
    return objective_location if objective_location else BoardLocation(-1, -1)


if __name__ == "__main__":
    run()
