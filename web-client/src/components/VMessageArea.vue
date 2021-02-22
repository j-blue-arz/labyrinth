<template>
    <div class="message-area" v-if="visible">{{ text }}</div>
</template>

<script>
import * as action from "@/model/player.js";

export default {
    name: "v-message-area",
    props: {
        countdown: {
            type: Object,
            required: true
        },
        userPlayer: {
            required: true
        }
    },
    computed: {
        text: function() {
            if (this.shouldShowMessage) {
                if (this.userPlayer.hasToShift()) {
                    return "Drag the maze tiles to modify the maze layout.";
                } else if (this.userPlayer.hasToMove()) {
                    return "Select a connected maze tile to move to.";
                }
            }
            return "";
        },
        visible: function() {
            return this.text !== "";
        },
        shouldShowMessage() {
            return (
                this.countdown.isRunning() &&
                this.countdown.remaining < this.countdown.startSeconds - 10
            );
        }
    }
};
</script>

<style lang="scss">
.message-area {
    --line-height: 1.2;
    --padding: 1rem;
    --font-size: 1.2rem;
    --num-lines: 3;

    @media (orientation: portrait) {
        --num-lines: 2;
    }

    padding: var(--padding);
    font-size: var(--font-size);
    line-height: var(--line-height);
    min-height: calc(var(--font-size) * var(--line-height) * var(--num-lines) + var(--padding) * 2);
    @include game-widget;
}
</style>
