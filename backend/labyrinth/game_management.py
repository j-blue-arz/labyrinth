""" This module provides a cli for game-management-related use cases."""
from datetime import timedelta

import click
from flask import Blueprint, current_app

from . import controller

GAME_MANAGEMENT = Blueprint("game-management", __name__, cli_group="game-management")


@GAME_MANAGEMENT.cli.command("remove-overdue-players")
@click.option("-s", "--seconds", type=int, default=60)
def cli_remove_overdue_players(seconds=60):
    _init_app()
    overdue_timedelta = timedelta(seconds=seconds)
    controller.remove_overdue_players(overdue_timedelta)


@GAME_MANAGEMENT.cli.command("remove-unobserved-games")
@click.option("-s", "--seconds", type=int, default=3600)
def cli_remove_unobserved_games(seconds=3600):
    _init_app()
    unobserved_period = timedelta(seconds=seconds)
    controller.remove_unobserved_games(unobserved_period)


def remove_overdue_players(seconds=60):
    overdue_timedelta = timedelta(seconds=seconds)
    controller.remove_overdue_players(overdue_timedelta)


def remove_unobserved_games(seconds=3600):
    unobserved_period = timedelta(seconds=seconds)
    controller.remove_unobserved_games(unobserved_period)


def _init_app():
    ctx = current_app.test_request_context()
    ctx.push()
    current_app.preprocess_request()
