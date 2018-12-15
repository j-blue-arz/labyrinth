# ADR 13: Architecture of computer players

## Context
One of the visions of the project is to investigate the complexity of the game and write artificial players who solve the problem of finding the best moves.

A first step towards this vision is to implement computer players, which play the game according to the rules. The opponent should find and play actions when it is his turn to do so.
More concrete, the requirements include
#### Adding computer players
A player should be able to add an opponent to the game. It should be made possible to watch computers play the game on their own. 

#### Multiple different algorithms
Right now, the only algorithm to add is to make random moves. In the future, more algorithms might be added. It should be possible to decide which one to use at run-time, so that different algorithms can be matched against each other.

#### Time restrictions
One NFR states that the time a computer searches for a move should be restrictable. A straightforward solution would be to have a thread compute a solution, and have another thread ask for a result after a specified time constraint. If no solution is ready, a random move is made.
The question if or how an algorithm could first compute a fallback action and then start computing another, better solution is not addressed here.

#### Update timeing
The idea of time restriction is that the player should not have to wait too long for the opponent to make a move. On the other hand, if the opponent settles on actions too fast, the player might miss the moves made. Hence the web-client should either be given time to update, or take its time to update itself.

#### Taking actions
If it is the computer player's turn to take actions, he should determine a valid shift and move action. The question is how an algorithm that computes these actions is informed that it has to run and with what state it has to run. 
One solution could be to implement the opponent as a process separated from the server. Then it could be run on any machine, and communicate with the server via API. To determine that it has to compute shifts or moves, it has to poll the state. This raises the problem of how to enforce the above mentioned time constraints, if there is no direct communication between server and opponent.
Another solution is to add the algorithm to the server code, where it is actively started as a separate thread. 
Then it is important that the computation only start after the current user thread has persisted the game. Otherwise, the new thread might alter the game before it is persisted. This could be eliminated by copying the entire state before starting the thread. The other problem is that the new thread could terminate and take actions before the user thread has persisted the game.

#### Computer player architecture
As always, information hiding and separation of concerns have to be respected. The game model should not know whether its players are human or computers. The algorithms only have to know the state of the board. The logic of timekeeping and submitting of actions should be separated from the actual computation algorithms. They further have to know the URL of the API methods and the game's and player's ID. The above mentioned constraint concerning the starting of the new thread is vital and has to be respected as well.
The question here is which entity should include the responsibility to start a computer player's move. This could be the Service Layer, but there should not be too much logic there. Another entity is the player, which could be represented by a class on its own, `Player`. This class can then be subclassed for computer players, but then there remains the question of how to know that the persistence took place.
One interesting thought experiment here is: how would this work if there was no persistence and the game state would be kept in memory? In that case, the computer player could start computing as soon as previous actions change of state were complete. The turn logic would notify the player. Still, he would have to separate his game state from the previous thread's state, so that he does not alter the game state before transmission to the previous user.



#### Update the Game
After the action determining algorithm returns, it has to incorporate its actions into the game. If the algorithm is a separate process, it has to use the API methods. A thread running in the server can either alter the database directly, or call functions in the service layer. The former approach is less desirable, because it couples the opponent logic to the database calls. Both approaches have the problem that they would be performed by the newly started thread. But in a flask application, this thread does not have access to the flask thread-global storage, as it was not started by flask.
A third option is to let the new thread call the game API methods.

#### Construction and persistence of players
Up to now, the Game generates a player ID when a player is added. In the future, Players will have to be created by the mapper or the service layer, because Game does not know which Player to create. There remains the problem of finding the next ID for a Player on creation. This could either be done by the Game, with a function providing the next ID. Or the Game is passed a factory (e.g. a constructor) for a Player, with which it creates a Player, passing the ID. A third option is to disconnect Player and Game by implementing Player as a separate entity, with a table on its own. Then the database is responsible for creating globally unique IDs.

Another challenge is the persistence of a player, in view of subclassing. Fowler presents three possibilities in his book: single table inheritance, where all classes of a hierarchy are stored in the same structure, with fields left blank. Class table inheritance, where there is a table per class, which only includes the fields added in the respective subclass, and with foreign keys to parent classes. Concrete table inheritance, where there is one table per concrete class in the hierarchy, including all fields of this class and its parent classes. In the terms of JSON persistence, this translates to either one JSON type with optional fields, or two JSON types where one links to the other with an ID, or two JSON types which are completely separate.

#### Required references
There is an interesting question whether the graph of object dependencies should be a tree or is allowed to be a DAG. Up to now, in the back-end, it is a tree: there are no two paths of references from one object to another. Adding a reference from a Player to a Piece adds another chain of references from a Game to the Piece. Game to Board to Piece and Game to Players to Piece. In the web-client, there is even less restrictions, due to the presence of directed cycles: the pieces have a reference to their maze card, and the maze card has a list of the pieces standing on it. From tree to DAG to cycles, the complexity increases, and so does the required effort to keep everything in sync. The advantage can be easier access to objects due to the added references.
Is it possible to get rid of one of the references in the structure of Players, Games, Pieces and Boards? The list of Player in Game is required because the Game's interface uses player IDs. The Player needs a reference to the Board because the ComputerPlayer needs it to compute actions. The reference of a Player to a Piece could be eliminated by sharing an ID, but this introduces just another way of representing an existing dependency.

## Decision
I will alter the service method with which to add players, and include a parameter to decide if the player is human or not. The web-client will have options to add computer players, or (at most once) add himself as a player. The latter is no longer an automatism.

The Game currently only has player IDs. I will encapsulate these in a Player class. Each player will have a reference to the Board he is currently playing, and to its Piece on the Board. The Turn logic uses the new Player objects instead of IDs. It informs a Player when it is his turn to play. The Game will no longer create the players. The service layer creates players and adds them to the game. The Game will be passed a constructor of a Player class, and use it to set the ID. This is a simple solution, which is good enough as long as there is no need for a globally unique player ID.

The Player is subclassed for computer players (ComputerPlayer). The logic for time-keeping and submitting actions is implemented in this subclass. I don't think there is a need for another layer between the ComputerPlayers and the algorithms. It suffices to implement the ComputerPlayer class and the algorithms together in a separate module. The ComputerPlayer will have a field specifying its algorithm. The best option here is to directly reference an Algorithm class. I think it is best to encapsulate the algorithms in classes, as this makes it easy to keep state (maze) between sub-functions, and also enables the ComputerPlayer to ask the algorithm for moves instead of haveing to wait. The algorithms will share an interface.

Both the ComputerPlayer and the Algorithm have to run in a separate thread. The ComputerPlayer, because it must not block the flask thread handling the starting user interaction. The Algorithm, to enable time-keeping in the ComputerPlayer. If the Algorithm does not answer in time, the ComputerPlayer asks the RandomActionDeterminer, the most basic Algorithm implementation, as a fallback. When notified to take action, the ComputerPlayer will first fetch all necessary information, like the return URLs and the game state, then start a new thread for itself. It will deep copy all state, so that the original state is not altered. I will take no further measures to make sure that the ComputerPlayer does not send POSTs to the API before the previous thread has finished. I expect the locking mechanisms of the database on the one hand, and the minimum time restriction on the other hand, to take care that there is no lost update problem. Even if there was, the validation of user actions would make sure that the persisted game is not left in an in inconsistent state.
I will further implement a method to start a database transaction as soon as the state is fetched for alteration, i.e. in a POST method call.
If this ever becomes a problem, I would have to pull the turn logic into the service layer.

Remove ID in Piece. In setter of Board in Player, let Player register in Board. Board returns Piece. Do this during init_game. 

Both Player and ComputerPlayer will be stored in JSON as a single type. The ComputerPlayer will be recognizable because it has added fields isComputer and algorithm.

I will also rename package `domain` into `model`, and rename module `model` into `game`.


## Status
Ready to be implemented.

## Consequence
Refactor, revisit this ADR if necessary.





