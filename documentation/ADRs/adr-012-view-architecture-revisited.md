# ADR 12: Vue behaviour, with API communication.

## Context
This ADR deals with the currently required Vue components and their interaction. The last step in the implementation was to connect the VueJS application to the backend API. The next step is to refactor the implementation, with the goal to separate the API communication from the game logic. This ADR builds on ADR 5.

A common design decision for Vue applications is to distinguish between presentational and container components. Presentation components are concerned with how things look, container components with how things work. The former receive data with props, and send signals with $emit. The latter listen to these signals, mutate their own state and forward it as data props to the presentational components. The presentational components never mutate state directly.
VueJS has a framework, Vuex, which implements this pattern.

One question is how the game logic defining component, currently the `GameContainer`, and the API communication are related. Is the API communication a Vue component of its own, or will it be simple JS class? Will it be a member of the `GameContainer`, or will it be an outer layer around the `GameContainer`?

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

API methods in separate module. How much of API handling should be in this module? At least the method calls. These calls return Promises, i.e. callbacks. So a user has to provide a callback. Maybe also transformation between response and state, and/or error handling. Error handling should be done by a Vue component, as it might have to interact with the user. `GameContainer` uses 2d-matrix of maze cards, API has a list of maze cards which include their location.

A few ideas:
API methods in separate module. This can be mocked by tests.
A smart component outside of the `GameContainer` will interact with the API. This new component (working name: `OnlineGame`) will handle errors and transformation. `GameContainer` might not emit own events, instead `OnlineGame` will listen to the same ones. `GameContainer` will update view on events, while `OnlineGame` calls API method on events.
Pull game logic out of `GameContainer` into game class. Where is this class created? 
`OnlineGame` can build the game from API and pass it down to the `GameContainer` by props. `GameContainer` updates its components with the state of this game. If `GameContainer` calls methods on this game? This is bad practice as `GameContainer` in this way mutates state which it does not own. 

If prop is not set on `GameContainer`, it can call a game factory (another class) to generate a game randomly. This way, tests can set their own game. Existing tests written up to now can use the same factory.

There remains the conflict between the two ways the game state is changed, one by direct manipulation and one by API updates.

`OnlineGame` is not required to be a Vue component. Instead, it can just be a plain old class.

Resources:
https://medium.com/@dan_abramov/smart-and-dumb-components-7ca2f9a7c7d0
https://itnext.io/how-to-structure-a-vue-js-project-29e4ddc1aeeb
https://vuex.vuejs.org/guide/structure.html
https://github.com/vuejs/vuex/tree/dev/examples/shopping-cart

## Decision
Keep it simple, no Vuex (yet).
API methods will be implemented in separate module `gameApi`. This module handles the calls only, users have to supply parameters and callbacks.
There is no need for `OnlineGame` to be a Vue component. Instead, I will implement plain JS classes. The class `game` represents the current state of a game. It has methods to alter that state, such as shifting and moving. The class `randomGameFactory` will create an initial state randomly. The component `GameContainer` will either use this factory, if supplied by props, or try to connect to the server and build the game itself. This way, tests can either work with a mock factory or also supply the `randomGameFactory`. The `GameContainer` will handle calling and polling the API (through `gameApi`), listen to events from the view and update the game.

I will keep track of the player ID with local storage (https://vuejs.org/v2/cookbook/client-side-storage.html): if an ID can be found in local storage, I use it to GET the state. If this returns an error, or if no ID was found in local storage, I connect to the server to get a new ID by adding a player (POST).

To handle the polling problem, all axios GET requests will be given a token (see https://github.com/axios/axios). On a POST request, the GET requests are cancelled. The polling timer is cancelled as well. On return a single GET is issued and the timer is started.

## Status
To be implemented.

## Consequence
Refactor, revisit this ADR if needed.



