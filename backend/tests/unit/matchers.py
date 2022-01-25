from datetime import timedelta


def time_close_to(expected_time, delta_ms=500):
    """ works for both timedelta and timestamps"""
    class Matcher:
        def __init__(self, expected_time, delta_ms):
            self.expected_time = expected_time
            self.delta = timedelta(milliseconds=delta_ms)

        def __eq__(self, other_time):
            matches = self.expected_time - other_time < self.delta
            if matches:
                return True
            else:
                raise AssertionError(f"expected: time close to {self.expected_time}, got {other_time}")
    return Matcher(expected_time, delta_ms)


def timedelta_close_to(expected_timedelta, error_ms=500):
    class Matcher:
        def __init__(self, expected_timedelta, error_ms):
            self.expected_timedelta = expected_timedelta
            self.error = timedelta(milliseconds=error_ms)

        def __eq__(self, other_timedelta):
            matches = self.expected_timedelta - other_timedelta < self.error
            if matches:
                return True
            else:
                raise AssertionError(f"expected: timedelta close to {self.expected_timedelta}, got {other_timedelta}")
    return Matcher(expected_timedelta, error_ms)
