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
@click.option("--name", "-n", "names", multiple=True, required=True,
              type=str, help="Algorithm names of the provided benchmark_files, in the same order. \
                  Should be provided as often as there are benchmark files.")
def combine(benchmark_files, outfile, names):
    dfs = [pd.read_csv(infile) for infile in benchmark_files]
    dfs = [clean_times(df, name) for df, name in zip(dfs, names)]
    df = combine_benchmark_results(dfs)
    df[["size", "depth"]] = df["instance"].str.extract(".*_s([0-9]+).*_d([0-9]+).*")
    df.to_csv(outfile)


@cli.command()
@click.argument('benchmark_csv')
@click.argument('outimage')
@click.option("--nrows", default=2, show_default=True)
@click.option("--ncols", default=2, show_default=True)
@click.option("--algo_name", default="libexhsearch", show_default=True)
def plot(benchmark_csv, outimage, nrows, ncols, algo_name):
    df = pd.read_csv(benchmark_csv)
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


if __name__ == "__main__":
    cli()
