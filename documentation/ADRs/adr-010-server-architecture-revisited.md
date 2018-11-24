# ADR 10: Refactoring server architecture

## Context
This ADR complements ADR 8.

Now that the integration tests for the application backend are green, it is time to refactor.
The modules which make up the backend so far are:
* The API, which handles the HTTP request and responses
* The Domain Model, which models the game rules
* A DTO Mapper, which maps between Domain Model and simple Json-ready structures
* A database module, which manages the connection to the database
* A service module (Service Layer), which keeps it all together.

The goal of the refactoring are simple, well-defined responsibilities for each module and a directed, acyclic graph of depencies between them.
The parsing of exception messages should be avoided. There should be a strict separation between the Domain Model and the Service Layer.
The interfaces between the modules should be clear and consistent.


### Tasks
#### Exception Handling
Currently, the Domain Model either raises exceptions or returns None for invalid requests. 
There are no custom exceptions, the Domain Model always raises ValueError with different messages. 
The Service Layer catches these exceptions, parses the message and raises a ApiException, which includes a key, a message and a HTTP status code.
These ApiException use the DTO Mapper to map themselves to a DTO. The API listens to these exceptions and transforms them to a HTTP response.

#### Database Access
The Service Layer always fetches the entire model, calls model methods and then persists the entire model.
Currently, the SQL queries for these operations (fetch, update, insert) for these tasks are hard coded in the service module for each operation.

## Decision
I am going to prefer the 'import module' style instead of 'from module import method'.
I am going to create two packages, one for the server application (`server`), containing the API, the Service Layer, the database access, the Mapper and the API Exceptions. This module knows that it is called via a HTTP API, it knows about the database and it also knows the Domain Model methods.
A second package will contain everything not related to the API (`domain`). It will be built in a way that it could also run in a completely different environment. It will include the Domain Model, domain-specific exceptions, and in the future also more domain logic such as routing, or turn management of a game.
The `domain` package will be contained in the `server` package. The latter will never depend on the former.
Each package defines its own exceptions. The `domain` package will define separate exceptions for each invalid operations. The service layer in `server` will map these to an instance of ApiException.

The API is responsible for the mapping between Json and DTOs.
The API depends only on the Service Layer and the API Exceptions. Both return datastructures in form of dictionaries and lists. They depend on the mapper to create these datastructures.
The Service Layer is the only module to alter the state of the Domain Model. The mapper has to know the Domain Model, as it maps its objects to DTOs. The database abstraction depends on the Domain Model as well.

The Service Layer uses an abstraction of a database. This abstraction is required, because the actual database might change in the future, both concerning the employed technology and the (table) layout. 
Right now, it stores Json strings in a single column of a relational database (Serialized LOB -- Large OBject). This keeps the mapping to database simple, because the hierarchical nature of the domain would require structural mapping patterns if one table for each domain object were used. As the way the model is persisted might change in the future, the database abstraction will encapsulate the whole process to store and load game instances. Currently, the sqlite3 database returns Record Sets on query, a structure representing a single row. The database abstraction has to map this Record Set to a game. This abstraction is hence a Table Data Gateway. Because the Domain Model is supposed to be independent of the database, Active Records, i.e. Domain Models which know how to update or find themselves in the database, are not an option.

The Domain Model will not know anything about its persistence in the database, nor about its results, states or exceptions beeing transmitted by the API.
## Status
Implemented

## Consequences
Refactor according to the made decisions. Amend this document if the decisions change during the refactoring.