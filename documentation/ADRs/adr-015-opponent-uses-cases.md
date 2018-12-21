# ADR 15: Computer opponent uses cases

## Context
There are several ways the game can be used. These use cases should all be covered by a simple UI. The use cases are:
1. Let a player play against a computer. This has to be the default. The computer should move first. If a player new to the game opens the UI for the first time, he should be able to quickly grasp the mechanics of the game. Hence, he should not have to setup the game. If he is the first player, a computer opponent should be present to *show* him what to do. One similar use case (1b) is that an advanced player wants to compete with a strong computer opponent. This might include switching the type of computer algorithm during play.
2. Let players play against each other. A second, third and fourth player should be able to join the game. One idea is to let the computer opponent vanish as soon as the second player joins. The first player should keep his starting position and color. One should keep in mind that this second player might be new to the game himself, and require the first player to *show* him the mechanics. Another idea is to only remove the computer once the fourth player tries to join.
3. Let computer play alone
Developers want to be able to watch *their* algorithm perform alone.
4. Let computers play against each other.
Similar to use case 3, developers might want to create algorithms for matches with other algorithms.

Idea: Right click on my piece opens context menu with advanced requests:
* Remove all computers from game
* Let computer play for me


## Decision
I will implement the following advanced requests (UI and back-end):
* Remove all computer players from the game
* Let a (specific) computer player play for me

This covers uses cases 1 through 4: 1 is the default, when the game is opened. For 2, a player has to join, and one of them can remove all computer opponents.
For 3, the first player can remove the computer opponent, and let a computer play for himself. For 4, the first player lets a computer play for himself directly.

The UI will have a context menu, available when the user right-clicks on his piece.
The back-end will have a method (DELETE) to remove a player from the game, regardless of whether this player is a computer.
The GET state response will include information about the type of player (human or algorithm), so that the web-client can remove all computers with multiple DELETE requests.
It will be possible to alter a player resource (PUT), by providing the same body as in the add player request.

Everytime a player is added or replaced, the game is restarted.

In the future, I could also implement functionality to change the type of a computer player, to handle use case 1b. I will not let computer players vanish for now.

## Status
Ready to be implemented.

## Consequence
This effectively restricts the maximum number of players per game to three. 
This makes these advanced options only available for PC players.





