import { NO_ACTION } from "@/model/player.js";

export const state = () => ({
    timer: 0,
    remainingSeconds: 0,
    visible: false
});

const getters = {
    isRunning: state => {
        return state.timer !== 0;
    },
    timerShouldRun: (_, __, ___, rootGetters) => {
        const userPlayer = rootGetters["players/userPlayer"];
        if (userPlayer) {
            return userPlayer.nextAction !== NO_ACTION && rootGetters["game/isOnline"];
        } else {
            return false;
        }
    }
};
const actions = {
    restartCountdown({ state, commit, dispatch, getters, rootState }, newValue) {
        dispatch("stopCountdown");
        commit("resetRemainingSeconds", newValue);
        const timer = setInterval(() => {
            commit("countDown");
            if (state.remainingSeconds <= 0) {
                if (getters.timerShouldRun) {
                    const currentPlayerId = rootState.game.nextAction.playerId;
                    dispatch("players/removeClientPlayer", currentPlayerId, { root: true });
                }
                dispatch("stopCountdown");
                commit("clearRemainingSeconds");
            }
        }, 1000);
        commit("saveTimer", timer);
    },
    stopCountdown({ state, commit }) {
        if (state.timer !== 0) {
            clearInterval(state.timer);
            commit("clearTimer");
        }
    },
    nextActionUpdated({ state, dispatch, getters }, nextAction) {
        if (getters.timerShouldRun) {
            const remainingSecondsApi = nextAction?.remainingSeconds ?? 0;
            if (remainingSecondsApi >= state.remainingSeconds) {
                dispatch("restartCountdown", remainingSecondsApi + 1);
            }
        }
    }
};
const mutations = {
    saveTimer(state, timer) {
        state.timer = timer;
    },
    clearTimer(state) {
        state.timer = 0;
    },
    resetRemainingSeconds(state, seconds) {
        state.remainingSeconds = seconds;
    },
    clearRemainingSeconds(state) {
        state.remainingSeconds = 0;
    },
    countDown(state) {
        state.remainingSeconds--;
    }
};

export default {
    namespaced: true,
    state,
    getters,
    actions,
    mutations
};
