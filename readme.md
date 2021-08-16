# Labyrinth

Play it at [maze-solver.com](https://maze-solver.com).

Labyrinth is a family board game. This project aims to recreate the game as a online multiplayer game, develop understanding of the game's complexity and implement practical search algorithms. There is one major difference to the [original game](https://www.ravensburger.com/spielanleitungen/ecm/Spielanleitungen/Labyrinth_26448_GB.pdf): all players have the same objective.

The application includes a number of bots employing different solvers. They are either called by the backend as shared libraries or compiled to WebAssembly to be used by the web-client.

![A live game](.github/labyrinth.png)

# Run locally
Easiest with docker-compose:

    docker-compose up

This will compile everything and build two Docker images, one for the backend including the solver libraries, and one for the web-client served by nginx.

Open `localhost` in your browser. Edge and IE are not supported.

## Experiments
The folder `experiments` contains analysis and benchmarks for the algorithm implementations.
See [readme in experiments](experiments/readme.md) for further instructions.
