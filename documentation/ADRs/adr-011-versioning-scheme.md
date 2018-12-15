# ADR 11: Updating the project version number

## Context
This ADR deals with the project's version number. The question to answer is when and how to increase this number. 
Currently, the version is 0.0.2. The original idea was to increase the third number after every sprint of pivotaltracker.com (1 week). The second number was planned to increase after every milestone, such as MVP, IS2019, and so on. There was no plan for the first digit.

Up to now, I forgot to increase the number once out of three weeks into the project. The incrementation by sprint seems arbitrary to me, because features are not finished when a 'sprint' ends. Actually, the entire concept of a sprint feels wrong for a project where I am working alone. Furth

There are several versioning schemes out there. Some take the current year as a major version, such as CAS Merlin, or Ubuntu. Others release based on sprints, such as configuration4sales. TeX version number converges against pi. Some projects, such as Python, have very complicated schemes, to distinguish between release candidates, alpha or beta versions, include the build number or certain hotfixes. This seems over-the-top for my project. The PEP 440, defines a scheme of `[N!]N(.N)*[{a|b|rc}N][.postN][.devN]`.

Very common is the three digit version, to indicate the major, minor or patch significance of a change.

Projects have version numbers to distinguish between old and new version of a release. But I did not yet have a single actual release.
I think that a 1.0.0 version should indicate the the software works in every aspect. Further major versions would change the application significantly.

A common practice is to tag versions in Git.
The version number of a JavaScript project can be found in the package.json. 
For python projects, the topmost package `__init__.py` usually includes a `__version__` variable.

For the project management, have a look at https://www.pivotaltracker.com/n/projects/2222295

## Decision
This project will have a three digit version. The numbers will be given based on milestones. The last digit will change frequently, after each user story. But there will be no strict rule about this increase. Forgetting to increase is hence no big deal. The second digit will change after fulfillment of an epic. Currently, the only fully defined epic is the MVP. An epics which will be reached in the future is IS2019, but it is yet to be defined which user stories are included.
Some of the epics defined on pivotaltracker, e.g. 'UX', are not epics but ticket labels. These are not intended to ever be 'done'.
I will tag all versions in Git. 

## Status
Accepted

## Consequences
Update version number after current ticket to 0.0.3. Tag this version.