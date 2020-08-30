""" This module provides a cli for game-management-related use cases."""
from datetime import timedelta

import click
from flask import Blueprint

from . import controller

GAME_MANAGEMENT = Blueprint("game-management", __name__, cli_group="game-management")


@GAME_MANAGEMENT.cli.command("remove-overdue-players")
@click.option("-s", "--seconds", type=int, default=60)
def remove_overdue_players(seconds=60):
    overdue_timedelta = timedelta(seconds=seconds)
    controller.remove_overdue_players(overdue_timedelta)
