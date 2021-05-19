""" This module sends important events to InfluxDB.

To activate it, set the environment variables
ENABLE_INFLUXDB_LOGGING, INFLUXDB_URL, and INFLUXDB_TOKEN to appropriate values.
The InfluxDB instance is expected to have an org 'labyrinth' and a bucket 'game'."""

from datetime import datetime

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import ASYNCHRONOUS

from flask import g


def create_logger(url=None, token=None):
    if url is not None and token is not None:
        g.event_logger = InfluxLogger(url, token)
    else:
        g.event_logger = EventLogger()


def get_logger():
    if "event_logger" not in g:
        g.event_logger = EventLogger()
    return g.event_logger


class EventLogger():
    def add_game(self, *args, **kwargs):
        pass

    def remove_game(self, *args, **kwargs):
        pass

    def add_player(self, *args, **kwargs):
        pass

    def remove_player(self, *args, **kwargs):
        pass


class InfluxLogger(EventLogger):
    _GAME_COUNTER = "games"
    _PLAYER_COUNTER = "players"

    def __init__(self, url, token):
        self.org = "labyrinth"
        self.bucket = "game"
        token = token
        client = InfluxDBClient(url=url, token=token, org=self.org)
        self.write_api = client.write_api(write_options=ASYNCHRONOUS)

    def add_game(self, game_id, num_games=1):
        point = Point(self._GAME_COUNTER) \
            .tag("change", "add") \
            .field("game_id", game_id) \
            .field("value", 1) \
            .field("count_games", num_games) \
            .time(datetime.utcnow(), WritePrecision.NS)
        self.write_api.write(self.bucket, self.org, point)

    def remove_game(self, game_id, num_games=0):
        point = Point(self._GAME_COUNTER) \
            .tag("change", "remove") \
            .field("game_id", game_id) \
            .field("value", -1) \
            .field("count_games", num_games) \
            .time(datetime.utcnow(), WritePrecision.NS)
        self.write_api.write(self.bucket, self.org, point)

    def add_player(self, player_id, game_id, is_bot, num_players):
        player_type = "bot" if is_bot else "human"
        point = Point(self._PLAYER_COUNTER) \
            .tag("change", "add") \
            .tag("game_id", str(game_id)) \
            .tag("player_type", player_type) \
            .field("player_id", player_id) \
            .field("value", 1) \
            .field("count_game_players", num_players) \
            .time(datetime.utcnow(), WritePrecision.NS)
        self.write_api.write(self.bucket, self.org, point)

    def remove_player(self, player_id, game_id, num_players):
        point = Point(self._PLAYER_COUNTER) \
            .tag("change", "remove") \
            .tag("game_id", str(game_id)) \
            .field("player_id", player_id) \
            .field("value", -1) \
            .field("count_game_players", num_players) \
            .time(datetime.utcnow(), WritePrecision.NS)
        self.write_api.write(self.bucket, self.org, point)
