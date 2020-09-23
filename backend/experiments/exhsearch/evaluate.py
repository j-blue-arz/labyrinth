""" Provides commands to evaluate the results of one or multiple benchmarks.

There are two commands:
- combine takes multiple benchmark results (csv-files) and merges them based on the instance names.
- plot will read a benchmark result and create a boxplot, grouped by maze size and search depth.
- compare will plot the speedup between two benchmark results, grouped by maze size and search depth.
"""
import math
import re

import click
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def clean_times(df, algo_name):
    df = df.copy()
    pattern = re.compile(".*time.*")
    time_cols = [col for col in df.columns if pattern.fullmatch(col.lower())]
    df[algo_name] = df[time_cols].min(axis=1)
    other_cols = [col for col in df.columns if col not in time_cols]
    df = df[other_cols]
    return df


def combine_benchmark_results(dfs):
    result = dfs[0]
    for df in dfs[1:]:
        result = result.merge(df, on="instance")
    return result


@click.group()
def cli():
    pass


@cli.command()
@click.argument('benchmark_files', nargs=-1)
@click.argument('outfile', nargs=1)
@click.option("--algo_name", "-n", "names", multiple=True, required=True,
              type=str, help="Algorithm names of the provided benchmark_files, in the same order. \
                  Should be provided as often as there are benchmark files.")
def combine(benchmark_files, outfile, names):
    """ Takes multiple benchmark results (csv-files) and merges them based on the instance names.

    For each input file in BENCHMARK_FILES,
    the minimum of all columns containing the word 'time'
    will be contained in the OUTFILE as ALGO_NAME.
    """
    dfs = [pd.read_csv(infile) for infile in benchmark_files]
    dfs = [clean_times(df, name) for df, name in zip(dfs, names)]
    df = combine_benchmark_results(dfs)
    df[["size", "depth"]] = df["instance"].str.extract(".*_s([0-9]+).*_d([0-9]+).*")
    df.to_csv(outfile)


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
    time_range = np.arange(math.floor(df[algo_name].min()),
                           math.ceil(df[algo_name].max()) + 1)
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
        if plot_num % ncols == 0:
            ax.yaxis.set_label_position("right")
            ax.yaxis.tick_right()
    plt.savefig(outimage)


@cli.command()
@click.argument('benchmark_file')
@click.argument('outimage')
@click.option("--columns", "-n", "names", nargs=2, required=True,
              type=str, help="Two column names in the provided BENCHMARK_FILE. \
                  The speedup of the first column relative to the second one will be plotted.")
@click.option("--depths", default=None, type=str,
              help="A list of depths, comma-separated. If not provided, all depths are included.")
def compare(benchmark_file, outimage, names, depths):
    """ Reads a benchmark result file BENCHMARK_FILE containing at least two time columns
    and creates a plot showing the speedup, grouped by maze size and depth.
    """
    df = pd.read_csv(benchmark_file)
    df["speedup"] = df[names[1]] / df[names[0]]
    if depths:
        depths = [int(depth) for depth in depths.split(",")]
    else:
        depths = np.arange(df["depth"].min(), df["depth"].max() + 1)

    sizes = np.sort(df["size"].unique())
    ncols = len(depths)
    nrows = len(sizes)
    fig = plt.figure(figsize=(ncols*8, nrows*4))
    fig.suptitle(f"Speedup: $t_{{{names[1]}}}/t_{{{names[0]}}}$", fontsize=20)
    plot_num = 1
    for size in sizes:
        for depth in depths:
            speedup_data = df[(df["depth"] == depth) & (df["size"] == size)]
            ax = plt.subplot(nrows, ncols, plot_num)
            if not speedup_data.empty:
                speedup_data = speedup_data.sort_values("instance")
                x, y = list(zip(*enumerate(speedup_data["speedup"])))
                colors = [_color(value) for value in y]
                chart = ax.bar(x, y, width=0.9, color=colors)
                _label(ax, chart)
                speedup_limits = [0, df[(df["depth"] == depth) & (df["size"] == size)]["speedup"].max()]
                ax.set_ylim(speedup_limits)
                ax.set_xticks([])
            plot_num += 1
    all_axes = fig.get_axes()
    first_row = [ax for ax in all_axes if ax.is_first_row()]
    for depth, ax in zip(depths, first_row):
        ax.annotate(f"Search depth {depth}", xy=(0.5, 1), xytext=(0, 5),
                    xycoords='axes fraction', textcoords='offset points',
                    fontsize=16, ha='center', va='baseline')
    first_column = [ax for ax in all_axes if ax.is_first_col()]
    for size, ax in zip(sizes, first_column):
        ax.annotate(f"Maze size {size}", xy=(0, 0.5), xytext=(-ax.yaxis.labelpad - 5, 0),
                    xycoords=ax.yaxis.label, textcoords='offset points',
                    fontsize=16, ha='right', va='center',
                    rotation=90)
    fig.tight_layout()
    fig.subplots_adjust(left=0.05, top=0.9)
    plt.savefig(outimage)


def _color(value):
    if value > 1:
        return "green"
    else:
        return "red"


def _label(ax, bar_chart):
    """Attach a text label above each bar in *rects*, displaying its height."""
    max_height = max(rect.get_height() for rect in bar_chart)
    threshold = max_height / 2
    for rect in bar_chart:
        width = rect.get_width()
        height = rect.get_height()
        x = rect.get_x()
        x_text_pos = x + width / 2
        if height > threshold:
            y_text_pos = height * 0.95
            color = "white"
        else:
            y_text_pos = height * 1.05
            color = "black"
        text = f"{height:.2f}" if height < 10 else f"{height:.1f}"
        ax.annotate(text,
                    xy=(x_text_pos, y_text_pos),
                    ha="center", va="center", color=color)


if __name__ == "__main__":
    cli()
