<template>
    <div class="timer" :class="{ 'timer--invisible': !visible }">
        0<span class="timer__separator">:</span>{{ formatTime(remainingSeconds) }}
    </div>
</template>

<script>
import { NO_ACTION } from "@/model/player.js";

export default {
    name: "timer",
    data() {
        return {
            visible: false
        };
    },
    watch: {
        nextUserAction: function(newValue) {
            if (this.timerShouldRun()) {
                this.$store.dispatch("countdown/restartCountdown");
                this.visible = true;
            } else {
                this.visible = false;
                this.$store.dispatch("countdown/stopCountdown");
            }
        },
        numPlayers: function(newValue, oldValue) {
            if (oldValue === 1 && this.timerShouldRun()) {
                this.$store.dispatch("countdown/restartCountdown");
                this.visible = true;
            } else if (newValue === 1) {
                this.visible = false;
                this.$store.dispatch("countdown/stopCountdown");
            }
        },
        gameSize: function() {
            // this is a heuristic to detect a game restart
            // For the case where a game is restarted with a different size,
            // but the user turn does not change
            if (this.timerShouldRun()) {
                this.visible = true;
                this.$store.dispatch("countdown/restartCountdown");
            }
        },
        objectiveId: function() {
            // this is a heuristic to detect a game restart
            // For the case where a game is restarted with the same size,
            // but the user turn does not change
            // This heuristic might fail!
            if (this.timerShouldRun()) {
                this.visible = true;
                this.$store.dispatch("countdown/restartCountdown");
            }
        },
        remainingSeconds: function(newValue) {
            if (newValue <= 0 && this.timerShouldRun()) {
                this.removeCurrentPlayer();
            }
        }
    },
    computed: {
        gameSize: function() {
            return this.$store.state.board.mazeSize;
        },
        objectiveId: function() {
            return this.$store.state.game.objectiveId;
        },
        remainingSeconds: function() {
            return this.$store.state.countdown.remainingSeconds;
        },
        nextUserAction: function() {
            const userPlayer = this.$store.getters["players/userPlayer"];
            if (userPlayer) {
                return userPlayer.nextAction;
            } else {
                return NO_ACTION;
            }
        },
        numPlayers: function() {
            return this.$store.state.players.allIds.length;
        }
    },
    methods: {
        formatTime: function(seconds) {
            return ("0" + seconds).slice(-2);
        },
        removeCurrentPlayer: function() {
            const currentPlayerId = this.$store.state.game.nextAction.playerId;
            this.$store.dispatch("players/removeClientPlayer", currentPlayerId);
        },
        timerShouldRun: function() {
            return this.nextUserAction !== NO_ACTION && this.$store.getters["game/isOnline"];
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
