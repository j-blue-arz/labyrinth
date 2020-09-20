<template>
    <p class="timer" :class="{ 'timer--invisible': !visible }">
        00:{{ formatTime(remainingSeconds) }}
    </p>
</template>

<script>
import { setInterval, clearInterval } from "timers";
export default {
    name: "timer",
    props: {
        controller: {
            type: Object,
            required: true
        }
    },
    data() {
        return {
            visible: false,
            remainingSeconds: 0,
            maxTurnSeconds: 30
        };
    },
    watch: {
        userTurn: function(newValue) {
            if (newValue !== "NONE") {
                this.visible = true;
                this.restartTimer();
            } else {
                this.visible = false;
                this.stopTimer();
            }
        },
        gameSize: function() {
            // this is a heuristic to detect a game restart
            // For the case where a game is restarted with a different size,
            // but the user turn does not change
            if (this.userTurn !== "NONE") {
                this.visible = true;
                this.restartTimer();
            }
        },
        objectiveId: function() {
            // this is a heuristic to detect a game restart
            // For the case where a game is restarted with the same size,
            // but the user turn does not change
            // This heuristic might fail!
            if (this.userTurn !== "NONE") {
                this.visible = true;
                this.restartTimer();
            }
        }
    },
    computed: {
        userTurn: function() {
            let userPlayerId = this.controller.getPlayerManager().getUserPlayer();
            let player = this.controller.getGame().getPlayer(userPlayerId);
            if (player) {
                return player.getTurnAction();
            } else {
                return "NONE";
            }
        },
        gameSize: function() {
            return this.controller.getGame().n;
        },
        objectiveId: function() {
            return this.controller.getGame().objectiveId;
        }
    },
    methods: {
        formatTime: function(seconds) {
            return ("0" + seconds).slice(-2);
        },
        restartTimer: function() {
            this.stopTimer();
            this.remainingSeconds = this.maxTurnSeconds;
            this.timer = setInterval(() => this.countDown(), 1000);
        },
        countDown: function() {
            this.remainingSeconds--;
            if (this.remainingSeconds <= 0) {
                this.removeCurrentPlayer();
                this.stopTimer();
            }
        },
        stopTimer: function() {
            if (this.timer !== 0) {
                clearInterval(this.timer);
                this.timer = 0;
            }
        },
        removeCurrentPlayer: function() {
            let currentPlayerId = this.controller.getGame().nextAction.playerId;
            this.controller.removeManagedPlayer(currentPlayerId);
        }
    }
};
</script>

<style lang="scss">
.timer {
    font-size: 3rem;
    user-select: none;

    &--invisible {
        visibility: hidden;
    }
}
</style>
