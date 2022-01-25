import Vue from "vue";
import Vuex from "vuex";

import game from "./modules/game.js";
import board from "./modules/board.js";
import players from "./modules/players.js";
import countdown from "./modules/countdown.js";

Vue.use(Vuex);

let store = new Vuex.Store({
    modules: {
        game: game,
        board: board,
        players: players,
        countdown: countdown
    },
    strict: process.env.NODE_ENV !== "production"
});

store.watch(
    state => state.game.nextAction,
    nextAction => {
        store.dispatch("countdown/nextActionUpdated", nextAction);
    }
);

export default store;
