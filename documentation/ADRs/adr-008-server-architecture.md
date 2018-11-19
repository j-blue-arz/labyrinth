# ADR 7: Server language and framework

## Context
Layering is a good idea. But this is only a small project. Still, it has a complex logic. Required parts: an API, domain logic, and state handling.

## Decision
The API is a clean and lightweight Flask runner without any logic. It only handles security aspects, such as authentification or authorization. Requests are forwarded to a Service Layer, which is also only a thin facade. It maps the requests to domain objects, calls the respective method in the domain logic, and maps the results back to Data Transfer Objects (DTO). These objects have no Python class representation, but are built out of dictionaries and list, which in turn are easily convertable to structured text (Json or XML).
The Domain Model objects and the DTOs should be independet of each other. Hence, a Mapper implements the mapping between the two and decouples them in this way.
The entire logic is organized in a Domain Model. The state of the Domain Model has to be globally accessible for all players. Hence, it has to be either kept in memory or persisted to a database.

## Status
Accepted

## Consequences
Decide how to keep the state between API calls.