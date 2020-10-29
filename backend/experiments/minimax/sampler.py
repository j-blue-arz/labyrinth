import threading
import time

import labyrinth.model.external_library as external


def observe_search_status(library, board, limit_timedelta, observe_timedelta):
    """ Runs the external library algorithm on the given instance, yields the current search status in regular
    time intervals.

    The yielded values are the current sample time (in fractional seconds), the depth and the termination status. """
    library_binding = external.ExternalLibraryBinding(library, board, board.pieces[0])
    search_ended_event = threading.Event()
    concurrent_library_binding = ConcurrentExternalLibraryBinding(
        library_binding, search_ended_event
    )
    sample_interval = observe_timedelta.total_seconds()
    limit_seconds = limit_timedelta.total_seconds()
    start = time.perf_counter()
    concurrent_library_binding.start()
    sample = 0.0
    sample_num = 1
    while sample < limit_seconds and not search_ended_event.is_set():
        next_sample = sample_num * sample_interval
        remaining = next_sample - sample
        time.sleep(remaining)
        search_status = library_binding.get_search_status()
        sample = time.perf_counter() - start
        yield sample, search_status["current_search_depth"], search_status["search_terminated"]
        sample_num += 1
    if not search_ended_event.is_set():
        library_binding.abort_search()
    search_ended_event.wait()
    search_status = library_binding.get_search_status()
    sample = time.perf_counter() - start
    yield sample, search_status["current_search_depth"], search_status["search_terminated"]


class ConcurrentExternalLibraryBinding(threading.Thread):
    def __init__(self, external_binding, search_ended_event):
        threading.Thread.__init__(self)
        self._external_binding = external_binding
        self._search_ended_event = search_ended_event
        self.action = None

    def run(self):
        self.action = self._external_binding.find_optimal_action()
        self._search_ended_event.set()
