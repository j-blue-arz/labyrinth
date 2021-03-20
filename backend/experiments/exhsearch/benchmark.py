""" This module runs benchmarks for an external library."""
import csv
import glob
import os
import timeit

import click

from experiments import serialization
import labyrinth.model.external_library as external


@click.command()
@click.option("--folder", "instance_folder", required=True)
@click.option("--outfile", required=True)
@click.option("--library", required=True)
@click.option("--pattern", default="*.json",
              help="Name of a specific test-case. If none given, all test-cases are run.")
@click.option("--repeats", default=5)
@click.option("--only-min/--all-values", default=True)
def benchmark_instances(instance_folder, outfile, library, pattern, repeats, only_min):
    instance_files = glob.glob(os.path.join(instance_folder, pattern))
    print(f"Running {len(instance_files)} benchmarks..")
    benchmark_results = [benchmark(library, repeats, instance_file=filename) for filename in instance_files]
    result = {name: value for name, value in benchmark_results}
    if only_min:
        result = {case_name: [min(values)] for case_name, values in result.items()}
    _write_csv(result, outfile)


def benchmark(library, repeats, instance_file):
    """ Runs the benchmark for the given test case.

    Reports <repeat> runs in seconds.
    """
    board, piece, name = _create_board_from_instance_file(instance_file)
    print(f"Running benchmark {name}..")
    optimizer = external.ExternalLibraryBinding(library, board, piece)
    return name, timeit.Timer(optimizer.find_optimal_action).repeat(repeats, 1)


def _create_board_from_instance_file(filename):
    board, instance_name = serialization.deserialize_instance_json(filename)
    return board, board.pieces[0], instance_name


def _write_csv(result_dict, outfile):
    with open(outfile, "w", newline='') as csvfile:
        repeats = len(next(iter(result_dict.values())))
        fieldnames = ["instance"] + [f"time{num}[s]" for num in range(repeats)]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for key, values in result_dict.items():
            out_dict = {f"time{num}[s]": values[num] for num in range(repeats)}
            out_dict["instance"] = key
            writer.writerow(out_dict)


if __name__ == "__main__":
    benchmark_instances()
