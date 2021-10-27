export const state = () => ({
    timer: 0,
    remainingSeconds: 0,
    startSeconds: 30
});

const getters = {
    isRunning: state => {
        return state.timer !== 0;
    }
};
const actions = {
    restartCountdown({ state, commit, dispatch }) {
        dispatch("stopCountdown");
        commit("resetRemainingSeconds");
        const timer = setInterval(() => {
            commit("countDown");
            if (state.remainingSeconds <= 0) {
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
    setDuration({ commit }, seconds) {
        commit("setDurationSeconds", seconds);
    }
};
const mutations = {
    setDurationSeconds(state, seconds) {
        state.startSeconds = seconds;
    },
    saveTimer(state, timer) {
        state.timer = timer;
    },
    clearTimer(state) {
        state.timer = 0;
    },
    resetRemainingSeconds(state) {
        state.remainingSeconds = state.startSeconds;
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
