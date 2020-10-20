""" Provides commands to compare the results of one or multiple benchmarks.

There are two commands:
- combine takes multiple benchmark results (csv-files) and merges them based on the instance names.
- compare will plot the speedup between two benchmark results, grouped by maze size and search depth.
"""
import re
import os
from operator import itemgetter

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
@click.option("--outfile", required=True)
@click.option("--algo_name", "-n", "names", multiple=True, required=True,
              type=str, help="Algorithm names of the provided benchmark_files, in the same order. \
                  Should be provided as often as there are benchmark files.")
def combine(benchmark_files, outfile, names):
    """ Takes multiple benchmark results (csv-files) and merges them based on the instance names.

    For each input file in BENCHMARK_FILES,
    the minimum of all columns containing the word 'time'
    will be contained in the OUTFILE as ALGO_NAME.
    """
    _combine(benchmark_files, outfile, names)


def _combine(benchmark_files, outfile, names):
    dfs = [pd.read_csv(infile) for infile in benchmark_files]
    dfs = [clean_times(df, name) for df, name in zip(dfs, names)]
    df = combine_benchmark_results(dfs)
    df[["size", "depth", "num"]] = df["instance"].str.extract(".*_s([0-9]+).*_d([0-9]+).*_num([0-9]+).*")
    df.to_csv(outfile)


@cli.command()
@click.argument('benchmark_file')
@click.argument('outimage')
@click.option("--columns", "-n", "names", nargs=2, required=True,
              type=str, help="Two column names in the provided BENCHMARK_FILE. \
                  The speedup of the first column relative to the second one will be plotted.")
@click.option("--depths", default=None, type=str,
              help="A list of depths, comma-separated. If not provided, all depths are included.")
@click.option("--normalize", type=click.Choice(["none", "all"], case_sensitive=False), required=False, default="none",
              help="Denotes which of the plots should be normalized to a common scale.\
                If 'none', all plots have a scale of their own.")
def plot(benchmark_file, outimage, names, depths, normalize):
    """ Reads a benchmark result file BENCHMARK_FILE containing at least two time columns
    and creates a plot showing the speedup, grouped by maze size and depth.
    """
    _plot(benchmark_file, outimage, names, depths, normalize)


def _plot(benchmark_file, outimage, names, depths=None, normalize=False):
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
    speedup_limits = [min(0.5, df["speedup"].min()), max(1.1, df["speedup"].max())]
    plot_num = 1
    for size in sizes:
        for depth in depths:
            speedup_data = df[(df["depth"] == depth) & (df["size"] == size)]
            ax = plt.subplot(nrows, ncols, plot_num)
            if not speedup_data.empty:
                speedup_data = speedup_data.sort_values("num")
                x = speedup_data["num"]
                values = speedup_data["speedup"]
                _basis_barchart(ax, x, values)
                if normalize == "none":
                    speedup_limits = [0, df[(df["depth"] == depth) & (df["size"] == size)]["speedup"].max()]
                ax.set_ylim(speedup_limits)
                ax.set_xticks(x)
                ax.set_xticklabels(x)
            plot_num += 1
    _label_depths(fig, depths)
    _label_maze_sizes(fig, sizes)
    fig.tight_layout()
    fig.subplots_adjust(left=0.05, top=0.9)
    plt.savefig(outimage)


@cli.command()
@click.argument("benchmarks_folder")
@click.argument("output_folder")
@click.option("--normalize", type=click.Choice(["none", "all"], case_sensitive=False), required=False, default="all",
              help="Denotes which of the plots should be normalized to a common scale.\
                If 'none', all plots have a scale of their own.")
def compare(benchmarks_folder, output_folder, normalize):
    """ COMBINE and PLOT.

    Reads all .csv files in BENCHMARKS_FOLDER,
    and combines them into a file benchmark_results.csv in the OUTPUT_FOLDER. The algorithm names are inferred from
    the original filenames.
    Then plots a comparison plot using the latest two algorithm names (by file age).
    The plot is saved in a file containing the latest algorithm name in the OUTPUT_FOLDER."""
    bench_files = _get_bench_files(benchmarks_folder)
    bench_files = _sort_by_modification_time(bench_files)
    names = _get_bench_names(bench_files)
    outfile = os.path.join(output_folder, "benchmark_results.csv")
    _combine(bench_files, outfile, names)
    outimage = os.path.join(output_folder, "speedup_" + names[0] + ".png")
    _plot(outfile, outimage, (names[:2]), normalize=normalize)


def _sort_by_modification_time(files):
    mod_times = [os.path.getmtime(f) for f in files]
    sorted_files = sorted(list(zip(files, mod_times)), key=itemgetter(1), reverse=True)
    return [file_tuple[0] for file_tuple in sorted_files]


def _get_bench_files(folder):
    folder_contents = list(os.listdir(folder))
    folder_paths = [os.path.join(folder, f) for f in folder_contents]
    folder_files = [f for f in folder_paths if os.path.isfile(f)]
    return [f for f in folder_files if f.endswith(".csv")]


def _get_bench_names(files):
    prefix_len = len(_longest_common_prefix(files))
    suffix_len = len(".csv")
    names = [f[prefix_len:-suffix_len] for f in files]
    return [name.replace("_", "-") for name in names]


def _longest_common_prefix(filenames):
    result = ""
    for chars in zip(*filenames):
        if len(set(chars)) == 1:
            result += chars[0]
    return result


def _label_depths(fig, depths):
    all_axes = fig.get_axes()
    first_row = [ax for ax in all_axes if ax.is_first_row()]
    for depth, ax in zip(depths, first_row):
        ax.annotate(f"Search depth {depth}", xy=(0.5, 1), xytext=(0, 5),
                    xycoords='axes fraction', textcoords='offset points',
                    fontsize=16, ha='center', va='baseline')


def _label_maze_sizes(fig, sizes):
    all_axes = fig.get_axes()
    first_column = [ax for ax in all_axes if ax.is_first_col()]
    for size, ax in zip(sizes, first_column):
        ax.annotate(f"Maze size {size}", xy=(0, 0.5), xytext=(-ax.yaxis.labelpad - 5, 0),
                    xycoords=ax.yaxis.label, textcoords='offset points',
                    fontsize=16, ha='right', va='center',
                    rotation=90)


def _color(value):
    if value > 1:
        return "green"
    else:
        return "red"


def _basis_barchart(ax, x, values, basis=1.0):
    """ A bar charts which is based not at 0 but at a different basis.

    Values lower than basis are depicted as bars stretching downwards,
    value higher than basis are depicted as bars stretching upwards. """
    colors = [_color(value) for value in values]
    bottoms = [basis if value > basis else value for value in values]
    heights = [value - basis if value > basis else basis - value for value in values]
    chart = ax.bar(x, heights, width=0.9, color=colors, bottom=bottoms)
    _label_basis_barchart(ax, chart, values)
    ax.axhline(basis, color="black", ls="--")


def _label_basis_barchart(ax, bar_chart, values):
    """Attach a text label to each bar, displaying its value."""
    for rect, value in zip(bar_chart, values):
        width = rect.get_width()
        x = rect.get_x()
        x_text_pos = x + width / 2
        y_text_pos = 0.95 if value > 1.0 else 1.05
        text = f"{value:.2f}" if value < 10 else f"{value:.1f}"
        ax.annotate(text,
                    xy=(x_text_pos, y_text_pos),
                    ha="center", va="center", color="black")


if __name__ == "__main__":
    cli()
