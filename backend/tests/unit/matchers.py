from datetime import timedelta


def timestamp_close_to(expected_timestamp, delta_ms=500):
    class Matcher:
        def __init__(self, expected_timestamp, delta_ms):
            self.expected_timestamp = expected_timestamp
            self.delta = timedelta(milliseconds=delta_ms)

        def __eq__(self, other_timestamp):
            matches = self.expected_timestamp - other_timestamp < self.delta
            if matches:
                return True
            else:
                raise AssertionError(f"expected: timestamp close to {self.expected_timestamp}, got {other_timestamp}")
    return Matcher(expected_timestamp, delta_ms)
