Labyrinth is a well-known german family board game. This project aims to recreate the game as a multiplayer game, develop understanding of the game's complexity and implement some computer opponents.

English manual to the game: https://www.ravensburger.com/spielanleitungen/ecm/Spielanleitungen/Labyrinth_26448_GB.pdf  
German manual to the game: https://www.ravensburger.de/spielanleitungen/ecm/Spielanleitungen/26446%20anl%201637944.pdf?ossl=pds_text_Spielanleitung

There is one major difference to the original game: all players have the same objective. 
The objective is always randomly chosen to be one of the 50 maze cards which is not occupied by a player's piece.

Also, it is only possible to reach an objective while making a move. Reaching an objective while it is another player's move is not counted.

## Installation
    cd web-client
    npm install
    npm run test:unit
    npm run build

I am aware that running the tests currently logs warnings to the console, but the tests pass nevertheless.      

    cd ../backend

Now is a good time to create and activate a virtual environment, e.g. on Linux:

    python -m venv venv
    . venv/bin/activate

install required packages:

    pip install -r requirements.txt
    python -m pytest ./tests

## Running server  
Flask comes with a built-in server, which is perfectly fine for testing and developement of algorithms

    cd ../backend
    export FLASK_APP=server
    flask run --port=5000

Open localhost:5000 in your browser. Edge and IE are not supported.

If you want the server to be visible in your local network:

    flask run --host=0.0.0.0 --port=5000

## Computer opponents
Use the game menu to set up a match containing computer players.

Currently, there is no option to add computer players. You can replace yourself by a computer player instead. So if you want to play against the computer,
or you want to let computer players play against each other, open the application in an additional tab (which adds another player) and replace yourself by an
algorithm of your choice.

## Benchmarks
    python -m benchmarking.bench_alpha_beta benchmark all

See the modules in backend/benchmarking for further instructions.
