# Labyrinth

Play it at [maze-solver.com](https://maze-solver.com).

Labyrinth is a family board game. This project aims to recreate the game as a online multiplayer game, develop understanding of the game's complexity and implement practical search algorithms. There is one major difference to the [original game](https://www.ravensburger.com/spielanleitungen/ecm/Spielanleitungen/Labyrinth_26448_GB.pdf): all players have the same objective.

![A live game](.github/labyrinth.png)

# Quick start
Build the client and run the flask web server.
## Build web-client
    cd web-client
    npm install
    npm run test:unit
    npm run build

    cd ../backend

Now is a good time to create and activate a virtual environment, e.g. on Linux:

    python -m venv venv
    . venv/bin/activate

install required packages:

    pip install -r dev-requirements.txt
    python -m pytest ./tests

## Running server  
Flask comes with a built-in server, which is perfectly fine for testing and development of algorithms

    cd ../backend
    export FLASK_APP=server
    flask run --port=5000

Open localhost:5000 in your browser. Edge and IE are not supported.

If you want the server to be visible in your local network:

    flask run --host=0.0.0.0 --port=5000

# Bots
Bots are implemented in C++. They are not required to run the game. They are either called by the backend as shared libraries or compiled to WebAssembly to be used by the web-client. See [readme in algolibs](algolibs/readme.md) for build steps.

## Experiments
The folder `experiments` contains analysis and benchmarks for the algorithm implementations.
See [readme in experiments](experiments/readme.md) for further instructions.
