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
            console.log(newValue);
            if (newValue !== "NONE") {
                this.visible = true;
                this.restartTimer();
            } else {
                this.visible = false;
                this.stopTimer();
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
                this.stopTimer();
            }
        },
        stopTimer: function() {
            if (this.timer !== 0) {
                clearInterval(this.timer);
                this.timer = 0;
            }
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
