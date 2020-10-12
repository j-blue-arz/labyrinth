import threading
import time
from datetime import timedelta
from random import randint

import click

import labyrinth.model.algorithm.external_library as external
from labyrinth.model import factories
from labyrinth.model.game import BoardLocation, Piece
from experiments import serialization


@click.group()
def cli():
    pass


@cli.command()
@click.option("--library", required=True)
@click.option("--outfolder", required=True)
def random(library, outfolder):
    for _ in range(100):
        board = generate_board(7)
        serialization.serialize_instance_json(board, outfolder, "instance")
        result = run_async(library, board, timedelta(seconds=3))
        print(result)


@cli.command()
@click.option("--library", required=True)
@click.argument('instance')
def run_file(library, instance):
    for _ in range(100):
        board, instance_name = serialization.deserialize_instance_json(instance)
        result = run_async(library, board, timedelta(seconds=3))
        print(f"{instance_name}: {result}")


def run_async(library, board, limit_timedelta):
    library_binding = external.ExternalLibraryBinding(library, board, board.pieces[0])
    search_ended_event = threading.Event()
    concurrent_library_binding = ConcurrentExternalLibraryBinding(library_binding, search_ended_event)
    concurrent_library_binding.start()
    time.sleep(limit_timedelta.total_seconds())
    library_binding.abort_search()
    search_ended_event.wait()
    return concurrent_library_binding.action


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


class ConcurrentExternalLibraryBinding(threading.Thread):
    def __init__(self, external_binding, search_ended_event):
        threading.Thread.__init__(self)
        self._external_binding = external_binding
        self._search_ended_event = search_ended_event
        self.action = None

    def run(self):
        self.action = self._external_binding.find_optimal_action()
        self._search_ended_event.set()


if __name__ == "__main__":
    cli()
