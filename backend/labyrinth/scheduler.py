"""Initialize scheduler."""

from flask import current_app
from flask_apscheduler import APScheduler

from labyrinth.game_management import remove_overdue_players, remove_unobserved_games

scheduler = APScheduler()
scheduler.api_enabled = False


def schedule_remove_overdue_players():
    app = scheduler.app
    if "OVERDUE_PLAYER_REMOVAL_INTERVAL_S" in app.config and "OVERDUE_PLAYER_TIMEDELTA_S" in app.config:
        interval = int(app.config["OVERDUE_PLAYER_REMOVAL_INTERVAL_S"])
        delta = int(app.config["OVERDUE_PLAYER_TIMEDELTA_S"])
        scheduler.add_job(id="remove-overdue-players",
                          func=_remove_overdue_players,
                          kwargs={"seconds": delta},
                          trigger="interval", seconds=interval)


def schedule_remove_unobserved_games():
    app = scheduler.app
    if "UNOBSERVED_GAMES_REMOVE_INTERVAL_S" in app.config and "UNOBSERVED_GAMES_TIMEDELTA_S" in app.config:
        interval = int(app.config["UNOBSERVED_GAMES_REMOVE_INTERVAL_S"])
        delta = int(app.config["UNOBSERVED_GAMES_TIMEDELTA_S"])
        scheduler.add_job(id="remove-unobserved-games",
                          func=_remove_unobserved_games,
                          kwargs={"seconds": delta},
                          trigger="interval", seconds=interval)


def _remove_overdue_players(seconds):
    with scheduler.app.app_context():
        _init_app()
        remove_overdue_players(seconds)


def _remove_unobserved_games(seconds):
    with scheduler.app.app_context():
        _init_app()
        remove_unobserved_games(seconds)


def _init_app():
    ctx = current_app.test_request_context()
    ctx.push()
    current_app.preprocess_request()
