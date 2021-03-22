""" Generates instances for minimax algorithm evaluation. """
from datetime import timedelta

import click
from tqdm import tqdm
from random import randint

import serialization
from minimax.sampler import determine_search_depth
from labyrinth.model import factories
from labyrinth.model.game import BoardLocation, Piece


@click.command()
@click.option("--outfolder", required=True)
@click.option("--library", required=True)
@click.option("--maze-size", "-ms", "maze_sizes", default=[7], multiple=True, show_default=True,
              type=int, help='Multiple values possible, e.g. -ms 7 -ms 9')
@click.option("--num_instances", default=100, show_default=True)
def generate_nontrivial(outfolder, library, maze_sizes, num_instances):
    """ Generates random minimax instances, where the objective cannot be reached with depth 1 """
    for maze_size in maze_sizes:
        print(f"generating instances for maze size {maze_size}")
        pbar = tqdm(total=num_instances)
        num_generated = 0
        while num_generated < num_instances:
            board = generate_board(maze_size)
            depth = determine_search_depth(library, board, limit_timedelta=timedelta(milliseconds=200))
            if depth > 1:
                serialize_instance_json(board, depth, num_generated, outfolder)
                num_generated += 1
                pbar.update(1)
        pbar.close()


def serialize_instance_json(board, depth, number, outfolder):
    maze_size = board.maze.maze_size
    instance_name = f"minimax_s{maze_size}_num{number}"
    serialization.serialize_instance_json(board, outfolder, instance_name)


def random_piece_location(board):
    def rand_location(maze_size):
        return BoardLocation(randint(0, maze_size - 1), randint(0, maze_size - 1))

    maze_size = board.maze.maze_size
    location = rand_location(maze_size)
    while board.objective_maze_card is board.maze[location]:
        location = rand_location(maze_size)
    return location


def generate_piece(board, identifier):
    location = random_piece_location(board)
    return Piece(identifier, board.maze[location])


def generate_board(maze_size):
    board = factories.create_board(maze_size=maze_size)
    board.pieces.append(generate_piece(board, 0))
    board.pieces.append(generate_piece(board, 1))
    return board


if __name__ == "__main__":
    generate_nontrivial()
