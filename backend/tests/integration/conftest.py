""" This module contains fixtures for end to end tests """
import glob
import os
import platform
import tempfile
import pytest

from labyrinth import create_app


@pytest.fixture
def app():
    """ Creates the app in test mode with a temporary database
    yields the app, and
    cleans up after the test
    """
    file_descriptor, db_path = tempfile.mkstemp()
    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
        "OVERDUE_PLAYER_TIMEDELTA_S": 30
    })
    yield app
    os.close(file_descriptor)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    yield app.test_client()


@pytest.fixture
def cli_runner(app):
    yield app.test_cli_runner()


def pytest_generate_tests(metafunc):
    if "library_path" in metafunc.fixturenames:
        extension = "*.so"
        if platform.system() == "Windows":
            extension = "*.dll"
        filenames = glob.glob("instance/lib/" + extension)
        metafunc.parametrize("library_path", filenames)
