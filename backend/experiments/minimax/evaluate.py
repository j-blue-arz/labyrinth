""" Cleans, evaluates and plots the results of the depths.py sampling """
import math

import click
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


@click.group()
def cli():
    pass


@cli.command()
@click.option("--decimals", default=1)
@click.argument("infile")
@click.argument("outfile")
def increments(infile, outfile, decimals):
    """ Given the result of a depths.py sample run as INFILE, this method will
    extract the increments in search depths and write them to OUTFILE.
    """
    df = pd.read_csv(infile)
    df["achieved_depth"] = np.where(df["terminated"], df["depth"], df["depth"] - 1)
    df["depth_change"] = df["achieved_depth"].diff()
    df["sample"] = df["sample"].round(decimals)
    instances = df["instance"].unique()
    rows = [_extract_increments_for_instance(instance, df) for instance in instances]
    result_columns = _determine_result_columns(df)
    result = pd.DataFrame(rows, columns=result_columns)
    result.to_csv(outfile)


def _determine_result_columns(df):
    depth_range = range(df["achieved_depth"].min(), df["achieved_depth"].max() + 1)
    return ["instance", "mazesize"] + [f"time_depth_{d}" for d in depth_range]


def _extract_increments_for_instance(instance, df):
    instance_df = df[df["instance"] == instance].sort_values(by="sample")
    result = {"instance": instance, "mazesize": instance_df["mazesize"].iloc[0]}
    label, time = _get_increment(list(instance_df.itertuples())[0])
    result[label] = time
    for sample_row in instance_df[instance_df["depth_change"] == 1].itertuples():
        label, time = _get_increment(sample_row)
        result[label] = time
    return result


def _get_increment(sample_row):
    depth = sample_row.achieved_depth
    label = f"time_depth_{depth}"
    time = round(sample_row.sample, 2)
    return label, time


@cli.command()
@click.argument("infile")
@click.argument("outimage")
@click.option("--threshold", default=3.0, show_default=True,
              help="""A sample time point. A vertical line will be drawn at this point, it
              will be annotated with the number of achieved depth up to this sample point""")
@click.option("--min", "min_time", default=0.1, show_default=True)
@click.option("--max", "max_time", default=10.0, show_default=True)
def plot(infile, outimage, threshold, min_time, max_time):
    """ Given the result of a increments run as INFILE, this method will plot
    the aggregated increments by maze size as boxplots and write them to OUTIMAGE.
    """
    df = pd.read_csv(infile)
    time_columns = [col for col in df if col.startswith("time_depth_")]
    for time_column in time_columns:
        df[time_column] = np.log10(df[time_column])
    min_time, max_time = np.log10(min_time), np.log10(max_time)
    threshold = np.log10(threshold)
    time_x_ticks = _compute_time_ticks(min_time, max_time, threshold)
    _fill_nans(time_columns, df, min_time)
    sizes = np.sort(df["mazesize"].unique())
    depths = _extract_depths(time_columns)
    fig = plt.figure(figsize=(10.0, len(sizes)*2.5))
    for index, size in enumerate(sizes):
        plot_num = index + 1
        ax = plt.subplot(len(sizes), 1, plot_num)
        for depth in depths:
            times = _get_times(df, depth, size)
            y = [depth] * len(times)
            ax.scatter(times.tolist(), y)
        _draw_threshold(ax, threshold, depths, size, df)
        ax.set_ylabel("Achieved depth")
        ax.set_title(f"Maze size {size}")
        ax.set_xlabel("Search time [s]")
        ax.set_xticks(time_x_ticks)
        ax.set_xticklabels(np.round(10.0**time_x_ticks, 1))
        ax.set_yticks(depths)
        ax.set_yticklabels(depths)
        ax.set_xlim([min_time, max_time])
    fig.tight_layout()
    plt.savefig(outimage)


def _draw_threshold(ax, threshold, depths, size, df):
    ax.axvline(threshold, color="red", ls="--")
    for depth in depths:
        times = _get_times(df, depth, size)
        num_lower = times[times < threshold].count()
        yoffset = -0.2 if depth > 1 else 0.0
        ax.annotate(str(num_lower), xy=(threshold, depth+yoffset), xytext=(threshold-0.1, depth+yoffset),
                    ha="right", va="center", arrowprops={"arrowstyle": "<-"})


def _get_times(df, depth, mazesize):
    time_column = f"time_depth_{depth}"
    return df[df["mazesize"] == mazesize][time_column].dropna()


def _fill_nans(time_columns, df, min_time):
    for col1, col2 in reversed(list(zip(time_columns, time_columns[1:]))):
        mask = df[col2].notna()
        df.loc[mask, col1] = df.loc[mask, col1].fillna(min_time)


def _extract_depths(time_columns):
    prefix_len = len("time_depth_")
    return [int(col[prefix_len:]) for col in time_columns]


def _compute_time_ticks(min_time, max_time, threshold):
    time_x_ticks = np.arange(math.floor(min_time)*1.0,
                             math.ceil(max_time)*1.0 + 1)
    time_x_ticks = np.insert(time_x_ticks, 1, threshold)
    time_x_ticks = np.insert(time_x_ticks, 1, max_time)
    time_x_ticks = np.sort(time_x_ticks)
    return time_x_ticks


if __name__ == "__main__":
    cli()
