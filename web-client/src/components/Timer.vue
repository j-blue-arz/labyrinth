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
            visible: false
        };
    },
    watch: {
        userTurn: function(newValue, oldValue) {
            if (newValue !== "NONE") {
                this.countdown.restartCountdown();
                this.visible = true;
            } else {
                this.visible = false;
                this.countdown.stopCountdown();
            }
        },
        gameSize: function() {
            // this is a heuristic to detect a game restart
            // For the case where a game is restarted with a different size,
            // but the user turn does not change
            if (this.userTurn !== "NONE") {
                this.visible = true;
                this.countdown.restartCountdown();
            }
        },
        objectiveId: function() {
            // this is a heuristic to detect a game restart
            // For the case where a game is restarted with the same size,
            // but the user turn does not change
            // This heuristic might fail!
            if (this.userTurn !== "NONE") {
                this.visible = true;
                this.countdown.restartCountdown();
            }
        },
        remainingSeconds: function(newValue) {
            if (newValue <= 0 && (this.userTurn === "MOVE" || this.userTurn === "SHIFT")) {
                this.removeCurrentPlayer();
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
        },
        countdown: function() {
            return this.controller.turnCountdown;
        },
        remainingSeconds: function() {
            return this.countdown.remaining;
        }
    },
    methods: {
        formatTime: function(seconds) {
            return ("0" + seconds).slice(-2);
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
