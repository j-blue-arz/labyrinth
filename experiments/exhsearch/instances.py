""" Generates instances for exhaustive search algorithm.

New instances can be generated with
    python instances.py --outfolder instances/ --library ../lib/libexhsearch.so

Try
    python instances.py --help
for further instructions
"""

import click
from tqdm import tqdm

from exhsearch import depths as exhsearch_depths
import serialization


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
    serialization.serialize_instance_json(board, outfolder, instance_name)


def serialize_instance_text(board, depth, number, outfolder):
    maze_size = board.maze.maze_size
    instance_name = f"exhsearch_s{maze_size}_d{depth}_num{number}"
    serialization.serialize_instance_text(board, outfolder, instance_name)


if __name__ == "__main__":
    run()
