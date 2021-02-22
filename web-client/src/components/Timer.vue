<template>
    <div class="timer" :class="{ 'timer--invisible': !visible }">
        0<span class="timer__separator">:</span>{{ formatTime(remainingSeconds) }}
    </div>
</template>

<script>
import { setInterval, clearInterval } from "timers";
import * as action from "@/model/player.js";

export default {
    name: "timer",
    props: {
        controller: {
            type: Object,
            required: true
        },
        countdown: {
            type: Object,
            required: true
        },
        userPlayer: {
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
            if (newValue !== action.NO_ACTION) {
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
            if (this.userPlayer.isHisTurn()) {
                this.visible = true;
                this.countdown.restartCountdown();
            }
        },
        objectiveId: function() {
            // this is a heuristic to detect a game restart
            // For the case where a game is restarted with the same size,
            // but the user turn does not change
            // This heuristic might fail!
            if (this.userPlayer.isHisTurn()) {
                this.visible = true;
                this.countdown.restartCountdown();
            }
        },
        remainingSeconds: function(newValue) {
            if (newValue <= 0 && this.userPlayer.isHisTurn()) {
                this.removeCurrentPlayer();
            }
        }
    },
    computed: {
        gameSize: function() {
            return this.controller.game.n;
        },
        objectiveId: function() {
            return this.controller.game.objectiveId;
        },
        remainingSeconds: function() {
            return this.countdown.remaining;
        },
        userTurn: function() {
            if (this.userPlayer) {
                return this.userPlayer.getTurnAction();
            } else {
                return action.NO_ACTION;
            }
        }
    },
    methods: {
        formatTime: function(seconds) {
            return ("0" + seconds).slice(-2);
        },
        removeCurrentPlayer: function() {
            let currentPlayerId = this.controller.game.nextAction.playerId;
            this.controller.removeManagedPlayer(currentPlayerId);
        }
    }
};
</script>

<style lang="scss">
.timer {
    height: 100%;
    font-size: 3rem;
    user-select: none;
    letter-spacing: 0.1em;
    display: flex;
    justify-content: center;
    align-items: center;

    &--invisible {
        visibility: hidden;
    }

    &__separator {
        font-size: 0.7em;
        font-weight: bold;
        vertical-align: middle;
    }
}
</style>
