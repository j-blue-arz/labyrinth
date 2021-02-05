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
    width: 12rem;
    padding: 1rem;
    font-size: 1.2rem;

    @include panel;
}
</style>
