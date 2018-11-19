## Vision
The application allows users to play the board game Labyrinth. 
The core loop is to find the minimal number of turns which allow the player to move his piece to his objective.
The player can either play alone, using a webbrowser, 

## Target user
The target users are all people who have fun playing the board game Labyrinth. The user has to have
access to a PC or smartphone to run the game in a webbrowser. A server is required to play the game with other players.

## Non-functional requirements
The non-functional requirements have different priorities. They can be seperated in requirements which are important before the IS2019 version, to be released in Januar 2019, and after this version.
### Pre-IS2019 requirements

#### Translation
* English only

#### Testability
* Integration Tests using web interface
* unit tests for the web service
* unit tests for the client

#### Platforms
* Client fully functional in IE 11, Firefox 62+, Chrome 69+ (browserslist: ie >= 11, Firefox >= 62, Chrome >= 69, not ie <= 8, > 1%)
* Client fully functional on my PC (i5-6500 @ 3.20GHz, 8.00 GB RAM, Windows 10 Pro 64 Bit)
* Client fully functional on HDTV Beamer (1280x720)
* Client fully functional on my Smartphone (Sony Xperia Z1 Compact, Android)
* Server requires python

#### Usability
* Usable on PC using mouse
* Usable on touchscreens

#### Code Quality
All identifiers and names in the English, with American spelling. Comments in English as well.
Focus on:
* Readability
* Maintainability
* Consistency
* Low dependencies
* No initial cost other than developing time

#### Style Guides
Vue.js code complies with https://vuejs.org/v2/style-guide/, Priority A rules.
Python code complies with PEP 8.
custom HTML element names comply with https://html.spec.whatwg.org/multipage/custom-elements.html#valid-custom-element-name

#### Accessibility
* Colors are chosen with respect to colorblindness
* Visual client has no special handling for visual impairments

#### Response time
* Client reacts 0.3 seconds after user interaction
* Client asks server at least every 2 seconds for updates
* Server responds at most 1s after receiveing a request
* Computer opponents answer after at maximum 3s

### Additional post-IS2019 requirements

#### Translation
* Open for adding translations, e.g. by adding a translation file for a language
* Translation in German

#### Code Quality
* Performance
* Security
* Robustness
* Stability

#### Response time
* Computer opponents respond time can be parameterized (defaults to 3s)

#### Open Source
The application is written with the goal to release the source code and all documentation to an open source platform.
Prior to such a release, legal concerns have to be checked.

#### Exception Handling
* No exceptions visible for user.
* Exceptions should be written to log, so that developers have hints on fixing potential bugs