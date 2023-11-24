import { defineStore } from "pinia";
import { useGameStore } from "@/stores/game.js";
import { usePlayersStore } from "@/stores/players.js";

import { NO_ACTION } from "@/model/player.js";


export const useCountdownStore = defineStore("countdown", {
    state: () => ({
        timer: 0,
        remainingSeconds: 0,
        visible: false,
    }),
    getters: {
        isRunning: (state) => state.timer !== 0,
        timerShouldRun: () => {
            const gameStore = useGameStore();
            const playersStore = usePlayersStore();
            const userPlayer = playersStore.userPlayer;
            if (userPlayer) {
                return userPlayer.nextAction !== NO_ACTION && gameStore.isOnline;
            } else {
                return false;
            }
        },
    },
    actions: {
        restartCountdown(newValue) {
            this.stopCountdown();
            this.resetRemainingSeconds(newValue);
            const timer = setInterval(() => {
                this.countDown();
                if (this.remainingSeconds <= 0) {
                    if (this.timerShouldRun) {
                        const playersStore = usePlayersStore();
                        const gameStore = useGameStore();
                        const currentPlayerId = gameStore.nextAction.playerId;
                        playersStore.removeClientPlayer(currentPlayerId, {
                            root: true,
                        });
                    }
                    this.stopCountdown();
                    this.clearRemainingSeconds();
                }
            }, 1000);
            this.saveTimer(timer);
        },
        stopCountdown() {
            if (this.timer !== 0) {
                clearInterval(this.timer);
                this.clearTimer();
            }
        },
        nextActionUpdated(nextAction) {
            if (this.timerShouldRun) {
                const remainingSecondsApi = nextAction?.remainingSeconds ?? 0;
                if (remainingSecondsApi >= this.remainingSeconds) {
                    this.restartCountdown(remainingSecondsApi + 1);
                }
            }
        },
        saveTimer(timer) {
            this.timer = timer;
        },
        clearTimer() {
            this.timer = 0;
        },
        resetRemainingSeconds(seconds) {
            this.remainingSeconds = seconds;
        },
        clearRemainingSeconds() {
            this.remainingSeconds = 0;
        },
        countDown() {
            this.remainingSeconds--;
        },
    },
});
