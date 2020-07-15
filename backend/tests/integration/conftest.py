""" This module contains fixtures for end to end tests """
import os
import tempfile
import pytest
from app import create_app


@pytest.fixture
def client():
    """ Creates the app in test mode with a temporary database
    yields a test client, and
    cleans up after the test
    """
    file_descriptor, db_path = tempfile.mkstemp()
    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
    })
    yield app.test_client()
    os.close(file_descriptor)
    os.unlink(db_path)
