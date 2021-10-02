import Vue from "vue";
import Vuex from "vuex";

import game from "./modules/game.js";
import board from "./modules/board.js";
import players from "./modules/players.js";
import countdown from "./modules/countdown.js";

Vue.use(Vuex);

export default new Vuex.Store({
    modules: {
        game: game,
        board: board,
        players: players,
        countdown: countdown
    },
    strict: process.env.NODE_ENV !== "production"
});
