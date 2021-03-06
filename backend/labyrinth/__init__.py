""" This package is the backend of the labyrinth game.
It serves the Vue application
and defines a set of API methods to play the game """
import mimetypes
import os

from flask import Flask
from werkzeug.middleware.profiler import ProfilerMiddleware


version_info = (0, 2, 2)
__version__ = '.'.join(map(str, version_info))


def create_app(test_config=None):
    """ basic Flask app setup. Creates the instance folder if not existing """
    app = Flask(__name__,
                instance_relative_config=True,
                static_folder="../static",
                static_url_path="")

    app.config.from_mapping(
        SECRET_KEY='dev',
        PROFILE=False,
        DATABASE=os.path.join(app.instance_path, 'labyrinth.sqlite'),
        LIBRARY_PATH=os.path.join(app.instance_path, 'lib'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    if app.config["PROFILE"]:
        app.wsgi_app = ProfilerMiddleware(app.wsgi_app, profile_dir=os.path.join(app.instance_path),
                                          stream=None)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import api
    app.register_blueprint(api.API)

    from . import game_management
    app.register_blueprint(game_management.GAME_MANAGEMENT)

    from labyrinth.database import DatabaseGateway
    app.before_first_request(lambda: DatabaseGateway.init_database())
    app.teardown_request(lambda exc: DatabaseGateway.close_database())

    mimetypes.add_type('application/wasm', '.wasm')

    @app.route('/')
    def index():
        """ Serves the 'static' part, i.e. the Vue application """
        return app.send_static_file("index.html")

    return app
