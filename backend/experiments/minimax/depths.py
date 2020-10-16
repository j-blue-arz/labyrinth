""" This module provides command line methods to record the search depth
by running time of the minimax algorithm. """
import csv
from datetime import timedelta
import glob
import os

import click
from tqdm import tqdm

from sampler import observe_search_status
from experiments import serialization


@click.group()
def cli():
    pass


@cli.command()
@click.option("--folder", "instance_folder", required=True)
@click.option("--outfile", required=True)
@click.option("--library", required=True)
@click.option("--pattern", default="*.json",
              help="Name of a specific test-case. If none given, all test-cases are run.")
@click.option("--limit", "limit_seconds", default=10.0, help="maximum search time in seconds")
@click.option("--interval", "sampling_interval", default=100, help="sampling interval in milliseconds")
def sample(instance_folder, outfile, library, pattern, limit_seconds, sampling_interval):
    """ Runs all instances in FOLDER for LIMIT seconds and samples the depth with the given sampling time INTERVAL. """
    instance_files = glob.glob(os.path.join(instance_folder, pattern))
    append = False
    num_samples = int(limit_seconds / sampling_interval * 1000)
    print(f"Running {len(instance_files)} instances, with at the maximum {num_samples} samples each.")
    instances_progress_bar = tqdm(total=len(instance_files))
    sampling_progress_bar = tqdm(total=limit_seconds)
    for filename in instance_files:
        board, instance_name = serialization.deserialize_instance_json(filename)
        maze_size = board.maze.maze_size
        result = []
        sampling_progress_bar.reset()
        for sample in observe_search_status(library, board,
                                            limit_timedelta=timedelta(seconds=limit_seconds),
                                            observe_timedelta=timedelta(milliseconds=sampling_interval)):
            sample_time, depth, terminated = sample
            result.append({"instance": instance_name,
                           "mazesize": maze_size,
                           "sample": sample_time,
                           "depth": depth,
                           "terminated": terminated})
            elapsed = min(sample_time, limit_seconds) - sampling_progress_bar.n
            sampling_progress_bar.update(elapsed)
        sampling_progress_bar.refresh()
        write_csv(result, outfile, append=append, fieldnames=["instance", "mazesize", "sample", "depth", "terminated"])
        append = True
        instances_progress_bar.update(1)
    instances_progress_bar.close()
    sampling_progress_bar.close()


def write_csv(result, outfile, append, fieldnames):
    mode = 'a' if append else 'w'
    print_header = not append
    with open(outfile, mode=mode, newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if print_header:
            writer.writeheader()
        for row in result:
            writer.writerow(row)


if __name__ == "__main__":
    cli()
