""" This module runs benchmarks for an external library.

There are two commands:
- testcases runs the instances defined in the tests,
- instances runs the instances from a given folder, defined by a json-format.
"""
import csv
import glob
import json
import os
import timeit

import click

from tests.unit.test_exhaustive_search import CASES_PARAMS
import labyrinth.model.algorithm.external_library as libexhsearch
import tests.unit.factories as setup


@click.group()
def cli():
    pass


@cli.command(name="testcases")
@click.option("--case", "case_name", default="",
              help="Name of a specific test-case. If none given, all test-cases are run.")
@click.option("--repeats", default=5)
@click.option("--outfile", required=True)
@click.option("--library", required=True)
@click.option("--only-min/--all-values", default=False)
def benchmark_testcases(case_name, repeats, outfile, library, only_min):
    cases = [case_name] if case_name else CASES_PARAMS.keys()
    benchmark_results = [benchmark(library, repeats, testcase_key=case_name) for case_name in cases]
    result = {name: value for name, value in benchmark_results}
    if only_min:
        result = {case_name: [min(values)] for case_name, values in result.items()}
    _write_csv(result, outfile)


@cli.command(name="instances")
@click.option("--folder", "instance_folder", required=True)
@click.option("--outfile", required=True)
@click.option("--library", required=True)
@click.option("--pattern", default="*.json",
              help="Name of a specific test-case. If none given, all test-cases are run.")
@click.option("--repeats", default=5)
@click.option("--only-min/--all-values", default=False)
def benchmark_instances(instance_folder, outfile, library, pattern, repeats, only_min):
    instance_files = glob.glob(os.path.join(instance_folder, pattern))
    print(f"Running {len(instance_files)} benchmarks..")
    benchmark_results = [benchmark(library, repeats, instance_file=filename) for filename in instance_files]
    result = {name: value for name, value in benchmark_results}
    if only_min:
        result = {case_name: [min(values)] for case_name, values in result.items()}
    _write_csv(result, outfile)


def benchmark(library, repeats, testcase_key=None, instance_file=None):
    """ Runs the benchmark for the given test case.

    Reports <repeat> runs in seconds.
    """
    if testcase_key:
        board, piece, name = _create_board_from_test_key(testcase_key)
    elif instance_file:
        board, piece, name = _create_board_from_instance_file(instance_file)
    print(f"Running benchmark {name}..")
    optimizer = libexhsearch.ExternalLibraryBinding(library, board, piece)
    return name, timeit.Timer(optimizer.find_optimal_action).repeat(repeats, 1)


def _create_board_from_test_key(key):
    param_dict = setup.param_tuple_to_param_dict(*(CASES_PARAMS[key]))
    board = setup.create_board_and_pieces(**param_dict)
    return board, board.pieces[0], key


def _create_board_from_instance_file(filename):
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
    return board, board.pieces[0], instance["name"]


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
    cli()
