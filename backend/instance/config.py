import os

""" The bots talk to the server via http to localhost.
Set this if the url should not be deduced from the request, but set fixed.
E.g. when running inside docker or behind a proxy. """
INTERNAL_URL = os.environ.get("INTERNAL_URL", default=None)

ENABLE_INFLUXDB_LOGGING = os.environ.get("ENABLE_INFLUXDB_LOGGING", default="False").lower() in ("true", "1", "t")
INFLUXDB_URL = os.environ.get("INFLUXDB_URL", default=None)
INFLUXDB_TOKEN = os.environ.get("INFLUXDB_TOKEN", default=None)

OVERDUE_PLAYER_TIMEDELTA_S = os.environ.get("OVERDUE_PLAYER_TIMEDELTA_S", default=30)
OVERDUE_PLAYER_REMOVAL_INTERVAL_S = os.environ.get("OVERDUE_PLAYER_REMOVAL_INTERVAL_S", default=15)
UNOBSERVED_GAMES_TIMEDELTA_S = os.environ.get("UNOBSERVED_GAMES_TIMEDELTA_S", default=3600)
UNOBSERVED_GAMES_REMOVE_INTERVAL_S = os.environ.get("UNOBSERVED_GAMES_REMOVE_INTERVAL_S", default=1800)
