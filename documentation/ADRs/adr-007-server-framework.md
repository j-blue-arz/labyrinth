# ADR 7: Server language and framework

## Context
Which language and framework to implement the server? Options: Java EE, Python, or Node. Node has advantage that front-end and back-end
could share implementation of logic. However, this might also result in a strong coupling between these two parts of the architecture.
Java EE comes with a lot of solutions to common problems like state management, asynchronous calls, contexts or persistence. However this seems to be to heavy-weight for such a small project.
Python + Flask is leightweight, but additional libraries or handmade solutions are required for more advanced techniques.

## Decision
I will implement the backend logic in Python. The web service will be implemented using Flask.
## Status
Accepted

## Consequences
The web service serves the Vue-Application as static content on the context-root. An additional API is required for the service calls.
Further challenges, such as state management, mapping between model and API, concurrency, and maybe persistence (with transactions) require further decisions.
If I run into bigger issues I will evaluate if there is a better fit.