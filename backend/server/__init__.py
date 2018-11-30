""" This package is the backend of the labyrinth game.
It serves the Vue application
and defines a set of API methods to play the game """
import os

from flask import Flask, render_template

version_info = (0, 0, 3)
__version__ = '.'.join(map(str, version_info))

def create_app(test_config=None):
    """ basic Flask app setup. Creates the instance folder if not existing """
    app = Flask(__name__,
                instance_relative_config=True,
                static_folder="../../dist/static",
                template_folder="../../dist")

    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'labyrinth.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import api
    app.register_blueprint(api.API)

    from . import database
    app.before_first_request(database.init_database)
    app.teardown_request(database.close_database)

    @app.route('/')
    def index():
        """ Serves the 'static' part, i.e. the Vue application """
        return render_template("index.html")

    return app
