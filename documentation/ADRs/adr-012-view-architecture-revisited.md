# ADR 12: Vue behaviour, with API communication.

## Context
This ADR deals with the currently required Vue components and their interaction. The last step in the implementation was to connect the VueJS application to the backend API. The next step is to refactor the implementation, with the goal to separate the API communication from the game logic. This ADR builds on ADR 5.

A common design decision for Vue applications is to distinguish between presentational and container components. Presentation components are concerned with how things look, container components with how things work. The former receive data with props, and send signals with $emit. The latter listen to these signals, mutate their own state and forward it as data props to the presentational components. The presentational components never mutate state directly.
VueJS has a framework, Vuex, which implements this pattern.

One question is how the game logic defining component, currently the GameContainer, and the API communication are related. Is the API communication a Vue component of its own, or will it be simple JS class? Will it be a member of the GameContainer, or will it be an outer layer around the GameContainer?

Another question is how and where the following required tasks are achieved:
* Polling the API for updates
* Transforming interface responses into view model (updates)
* Updating the view
* Handling user interaction
* Validation of user requests
* Sending user requests to API
* Handling state client-side: how does client know if it has to connect to a running game or register a new player?

The problem with polling: if an update (POST) request is sent while a fetch (GET) was already sent, the result of the GET request can reset the view, and only after the next GET request's return is the view updated to the correct new state. The requests have to coordinated.

Another requirement is testing. The application should be testable without the API.

API methods in separate module. How much of API handling should be in this module? At least the method calls. These calls return Promises, i.e. callbacks. So a user has to provide a callback. Maybe also transformation between response and state, and/or error handling. Error handling should be done by a Vue component, as it might have to interact with the user. GameContainer uses 2d-matrix of maze cards, API has a list of maze cards which include their location.

Resources:
https://medium.com/@dan_abramov/smart-and-dumb-components-7ca2f9a7c7d0
https://itnext.io/how-to-structure-a-vue-js-project-29e4ddc1aeeb
https://vuex.vuejs.org/guide/structure.html
https://github.com/vuejs/vuex/tree/dev/examples/shopping-cart

## Decision
Keep it simple, no Vuex (yet).
API methods in separate module.
This module handles the calls only. A smart component outside of the GameContainer will use this module to interact with the API. This new component (working name: OnlineGame) will handle errors and transformation. GameContainer might not emit own events, instead OnlineGame will listen to the same ones. GameContainer will update view on events, while OnlineGame calls API method on events.

Pull game logic out of GameContainer into game class. An instance of this class passed to the GameContainer by props. Then GameContainer calls methods on this game? This is bad practice as GameContainer in this way mutates state which it does not own. GameContainer updates its components with the state of this game. OnlineGame builds the game from API and passes it down to GameContainer. If prop is not set on GameContainer, it calls a game factory (another class) to generate a game randomly. Tests can set their own game. Tests up to now can use the same factory. Tests for online game can mock the API module.
There remains the conflict between the two ways the game state is changed, one by direct manipulation and one by API updates.

Handle keeping track of player ID with local storage (https://vuejs.org/v2/cookbook/client-side-storage.html): if an ID can be found in local storage, use it to GET state. If this returns an error, pr of no ID was found in local storage, get a new ID by adding a player (POST).

To handle the polling problem, give all axios GET requests a token (see https://github.com/axios/axios). On an POST request, cancel the GET request. Also cancel the current GET timer. On return issue a GET and also directly start the GET timer.

## Status
To be implemented.

## Consequence
Refactor, revisit this ADR if needed.



