# ADR 3: Implementing client with plain JavaScript, jQuery, or Vue.js?

## Context
The fronted should run in the browser, and single play should be possible without the need of a server. At the time of this writing, JavaScript is the way to go for dynamic webpages.
This also is also an opportunity for me to learn how to write applications in JavaScript. There exists a multitude of additional libraries and frameworks for client side JavaScript development.
This ADR discusses which one to choose.

The three choices are plain JavaScript, without any additional libraries, jQuery, and Vue.js. I do not consider Angular 2.0, as this seems too much to learn for a simple project like this.
As I do not have any experience, I have to rely on forums and quick-glance tutorials. 
For a first JavaScript project, experienced developers in forums recommend to learn plain JavaScript before using frameworks. 
jQuery makes implementation easier by reducing boilerplate code for manipulating the DOM or making Ajax request. 
It also facilitates cross-browser development because it handles the differences between browsers under the hood. It makes it possible to link data to DOM objects. 
This encourages to use the DOM as a data store, and hence makes separation of view and model difficult. 
It is widely used, more than Vue.js at the time of writing. Compared to Vue.js, it is more of a convenience library than a framework. However, it is recommended not to use the two of them at the same time.
Vue.js separates view and model. It is considered to be easy to learn, and is very popular, both among those who have used it and among those who want to use a new framework. 
HTTP requests require another library. Using a framework, the developer has less control over how the architecture should be built. It seems to me that using framework requires less work for client-side MVP. 
Without further investigation, it is unclear how difficult it is to get the client-server connection to work as I intend to do it. 
I aim for a strict separation of data and view, and I want the objects received by Ajax calls can be transformed before updating the view. I would also like to have one clear location for the entire model,
rather than splitting up the model onto each component.

(Further) sources to consider:
Comparison between jQuery and Vue.js: https://stackshare.io/stackups/jquery-vs-vue-js
Connect Four with JavaScript plain: https://codepen.io/coderontheroad/pen/GdxEo
Connect Four with Vue.js: https://rossta.net/blog/basic-connect-four-with-vuejs.html

## Decision
I will use Vue.js for the client. If I encounter problems which delay the project by more than two weeks, I will switch to jQuery-only.

## Status
Accepted

## Consequences
I have to find and read a tutorial which helps me understand the things I need quickly. The connect four game mentioned above is a good starting point,as it also separates the game state from the view.
It also links to a discussion between presentational and container components, which would help me with this separation.