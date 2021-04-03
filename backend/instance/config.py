import os

INFLUXDB_TOKEN = os.environ.get("INFLUXDB_TOKEN")
INFLUXDB_URL = os.environ.get("INFLUXDB_URL", default=None)
