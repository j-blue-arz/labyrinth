# ADR 1: Client-Server architecture

## Context
One of the most basic design question for any project, including this game, 
is whether to build a client-server architecture or a standalone client program.

With a standalone client, players have to share a single client to play the game. 
This might mean sharing a mouse and a monitor, or passing a smartphone around. Measures have to be taken to prevent seeing each other objectives.
Web multiplayer might be possible by connecting multiple clients directly to each other, 
in a peer to peer fashion. However, this is more difficult to realize than a classical client-server game.

The client-server architecture makes web multiplayer easy to implement. The server manages the state of the game.
Clients connect to the server, make actions and are updated over a web interface. Players are only informed about their objectives.
A disadvantage of the client-server model is that validation logic might have to be duplicated, once on the client and once on the server.
Losses of connection might be a problem and have to be taken care of for all players.
The connection to the server can be handled by a web service (e.g. RESTful), or websockets.

The client-server model might als mean that the project is written in several languages. 
A client would be most certainly written in JavaScript, as this is understood by every Browser, 
eliminating the need for client-side third-party libraries or runtime environments. However, as I am not so familiar with JavaScript,
I would refrain from writing the server, or any computer opponents, in JavaScript, and might use Java or Python instead.
This might also be of advantage, as it allows me develop my skills both in a JavaScript frontend framework and a Python backend framework.


## Decision
I will implement the game with a client-server architecture.

## Status
Accepted.

## Consequences
It will be possible to play the game using multiple clients. This will in turn improve user experience.

There will be some duplicated validation logic, but in the early stages of implementation, most importantly the MVP,
there will only be validation on one side.

The client might be written in a JavaScript framework, which will allow me to learn how these are used.
The server might use a Pyhton web framework, which also will broaden my horizon.
A computer opponent might also be written in a third language.