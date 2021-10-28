<template>
    <div class="message-area" :style="{ visibility: visible ? 'visible' : 'hidden' }">
        {{ text }}
    </div>
</template>

<script>
import * as action from "@/model/player.js";

export default {
    name: "v-message-area",
    computed: {
        text: function() {
            if (this.shouldShowMessage) {
                if (this.userPlayer.nextAction === action.SHIFT_ACTION) {
                    return "Drag the maze tiles to modify the maze layout.";
                } else if (this.userPlayer.nextAction === action.MOVE_ACTION) {
                    return "Select a connected maze tile to move to.";
                }
            }
            return "";
        },
        visible: function() {
            return this.text !== "";
        },
        shouldShowMessage() {
            const countdownState = this.$store.state.countdown;
            return (
                this.$store.getters["countdown/isRunning"] &&
                countdownState.remainingSeconds < countdownState.startSeconds - 10
            );
        },
        userPlayer: function() {
            return this.$store.getters["players/userPlayer"];
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

    user-select: none;
    padding: var(--padding);
    font-size: var(--font-size);
    line-height: var(--line-height);
    min-height: calc(var(--font-size) * var(--line-height) * var(--num-lines) + var(--padding) * 2);
    @include game-widget;
}
</style>
