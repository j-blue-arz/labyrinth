import Vue from "vue";
import Vuex from "vuex";

import game from "./modules/game.js";

Vue.use(Vuex);

export default new Vuex.Store({
    modules: {
        game
    },
    strict: process.env.NODE_ENV !== "production"
});
