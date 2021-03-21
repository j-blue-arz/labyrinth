""" Measures the correlation between maze size and required search depth.

Usage:
    python depths.py count --outfile temp.csv --library ../../instance/lib/libexhsearch.so
    python depths.py plot temp.csv depths.png

See
    python depths.py --help
for further instructions.
"""
import csv
import time
from random import randint

import click
from tqdm import trange
import pandas as pd
import matplotlib.pyplot as plt

from labyrinth.model.game import BoardLocation, Piece
from labyrinth.model import factories
from experiments.exhsearch import optimizers


def generate_board(maze_size):
    board = factories.create_board(maze_size=maze_size)
    location = BoardLocation(randint(0, maze_size-1), randint(0, maze_size-1))
    while board.objective_maze_card is board.maze[location]:
        location = BoardLocation(randint(0, maze_size-1), randint(0, maze_size-1))
    piece = Piece(0, board.maze[location])
    board.pieces.append(piece)
    return board


def determine_exhsearch_depths(board, library_path):
    optimizer = optimizers.CompletePathLibraryBinding(library_path, board)
    actions = optimizer.find_optimal_actions()
    return len(actions) // 2


@click.group()
def cli():
    pass


@cli.command()
@click.option("--outfile", help='Path to a .csv file', required=True)
@click.option("--maze-size", "-ms", "maze_sizes", default=[7], multiple=True, show_default=True,
              type=int, help='Multiple values possible, e.g. -ms 7 -ms 9')
@click.option("--runs", default=1000, show_default=True)
@click.option("--library", required=True)
@click.option("--append/--newfile", "append_outfile", default=False, show_default=True)
def count(maze_sizes, runs, outfile, library, append_outfile):
    start = time.time()
    new_file = not append_outfile
    for maze_size in maze_sizes:
        result = []
        print(f"Determining {runs} depths for maze size {maze_size}.")
        for _ in trange(runs):
            depth = determine_exhsearch_depths(generate_board(maze_size), library)
            result.append({"mazesize": maze_size, "depth": depth})
        write_csv(result, outfile, new_file)
        new_file = False
    end = time.time()
    print(f"Took {end - start}s.")


@cli.command()
@click.argument('infile')
@click.argument('outfile')
def plot(infile, outfile):
    fig, ax = plt.subplots()
    df = pd.read_csv(infile)
    depths = df["depth"].unique()
    maze_sizes = df["mazesize"].unique()
    width = 1 / (len(maze_sizes)+1)
    leftmost = ((len(maze_sizes)-1)/2.0 * width)
    for i, maze_size in enumerate(maze_sizes):
        maze_size_group = df.groupby("mazesize").get_group(maze_size)
        num_values = len(maze_size_group.index)
        percentages = maze_size_group.groupby("depth").count() / num_values * 100
        ax.bar(x=percentages.index-leftmost+i*width, height=percentages["mazesize"], width=width,
               label=f"size: {maze_size}")
    ax.set_ylabel('%')
    ax.set_xlabel("Search depth")
    ax.set_title('Distribution of exhaustive search depths')
    ax.set_xticks(depths)
    ax.set_xticklabels(depths)
    ax.legend()
    plt.savefig(outfile)


def write_csv(result, outfile, new_file):
    mode = 'w' if new_file else 'a'
    print_header = new_file
    with open(outfile, mode=mode, newline='') as csvfile:
        fieldnames = ["mazesize", "depth"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if print_header:
            writer.writeheader()
        for row in result:
            writer.writerow(row)


if __name__ == "__main__":
    cli()
