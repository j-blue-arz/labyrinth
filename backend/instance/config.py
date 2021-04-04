import os

INFLUXDB_URL = os.environ.get("INFLUXDB_URL", default=None)
INFLUXDB_TOKEN = os.environ.get("INFLUXDB_TOKEN", default=None)
