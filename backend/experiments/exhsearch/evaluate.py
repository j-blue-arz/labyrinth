""" Plots the result of an exhsearch benchmark.

There is one command:
- plot will read a benchmark result and create a boxplot, grouped by maze size and search depth.
"""
import math

import click
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


@click.group()
def cli():
    pass


@cli.command()
@click.argument('benchmark_file')
@click.argument('outimage')
@click.option("--nrows", default=2, show_default=True)
@click.option("--ncols", default=2, show_default=True)
@click.option("--algo_name", default="libexhsearch", show_default=True,
              help="The column in the csv-file which should be considered for the plot.")
def plot(benchmark_file, outimage, nrows, ncols, algo_name):
    """ Reads a benchmark result and creates a boxplot, grouped by maze size and search depth. """
    df = pd.read_csv(benchmark_file)
    df[algo_name] = np.log10(df[algo_name])
    min_time, max_time = math.floor(df[algo_name].min()), math.ceil(df[algo_name].max())
    time_range = np.arange(min_time, max_time + 1)
    depths = np.arange(df["depth"].min(), df["depth"].max() + 1)
    sizes = np.sort(df["size"].unique())
    _ = plt.figure(figsize=(ncols*4.8, nrows*6.4))
    for index, size in enumerate(sizes):
        plot_num = index + 1
        by_depth = dict(tuple(df[(df["size"] == size)].groupby("depth")[algo_name]))
        for depth in depths:
            if depth not in by_depth:
                by_depth[depth] = pd.Series()
        values = [by_depth[d] for d in sorted(by_depth)]
        ax = plt.subplot(nrows, ncols, plot_num)
        ax.boxplot(values)
        ax.set_ylabel("Search duration [s]")
        ax.set_title(f"Maze size {size}")
        ax.set_xlabel("Search depth")
        ax.set_xticks(depths)
        ax.set_xticklabels(depths)
        ax.set_yticks(time_range)
        ax.set_yticklabels(10.0**time_range)
        ax.set_ylim([min_time, max_time])
        if plot_num % ncols == 0:
            ax.yaxis.set_label_position("right")
            ax.yaxis.tick_right()
    plt.savefig(outimage)


if __name__ == "__main__":
    cli()
