# ADR 9: Persistence of game state on server

## Context
The back-end server manages states of several currently running games. These states have to be kept between API calls.
There are two solutions: one ist to keep the state in memory, the other to persist the state to a database.

Keeping the state in memory is not possible out-of-the-box with Flask.
The problem is that different request might be handled by different threads, and a global object accessed by multiple threads
requires thread-handling such as locking. Another problem is that an in-memory approach does not scale well.

In-memory state is possible with a game loop running in a game thread. Requests are added to its request queue.
Requests altering the state invalidate all other altering requests for the same game in the queue. This is correct for a turn-based game, at any point only one player can alter the state of the game, and the next player can only make a move after his client has been updated with the new state.
Game loop is well-suited for real-time requirements and high frequency updates. It is a good choice if the API were to be implemented with WebSockets in the future.

The other solution is to persist the object model into database after each request, and load it from database before the request. The serialization/deserialization is done in the Service Layer.
Such an approach is good for longer running games with low-frequency updates.
Still, there is a problem of concurrency. 
If a player tries to make a move when it is not his turn, his request might reach the database just after the previous player has finished his turn, resulting in a wrong interpretation of the request. 
If the client handles this case, this is only a problem with  malicious players.
A database can either be a relational table-based database, such as sqlite3, or a document database, such as MongoDB.
The mapping logic in the DTO Mapper can also map the entire game state to a Json-ready structure. That way, I can persist the entire Game in a document database.
Document databases usually do not provide ACID compliance. Isolation does not matter in a turn-based game: 
when processing a state altering request of a player, the game fetches the current state and checks if it is valid, i.e. it is the player's turn. 
This can only be true for one player at a time. 
On the other hand, when adding players to the game, the absence of isolation could result in more players than allowed.
It is also possible to store the JSON string as a single column in a relational table. While this is considered an anti-pattern, it is also an easy setup.
sqlite3 does not require a database server, only a library has to be included.


These are two very different approaches. Each has an influence on its surrounding architecture. Hence, it might be difficult to change the approach once I run into problems. 
## Decision
Easy solution first, more advanced, scalable and secure later!
I will use the database approach. I will reuse the DTO-Mapper to map the entire game state to a dictionary.
A first implementation will use sqlite3 to store this dictionary. The database will have one table with two columns: one for the game id and one for the entire game. Each game will be stored as one document in this column.
Later, I might add support for MongoDB. But right now, I strive for an easy solution, as the database persistence is not the main focus of this project. 

## Status
Accepted

## Consequences
Install and use git before starting one of the two approaches.