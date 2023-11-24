<template>
    <div class="timer" :class="{ 'timer--invisible': !visible }">
        0<span class="timer__separator">:</span>{{ formatTime(remainingSeconds) }}
    </div>
</template>

<script>
import { mapState } from 'pinia';
import { useCountdownStore } from '@/stores/countdown.js';


export default {
    name: "countdown-timer",
    computed: {
        visible: function () {
            return this.timerShouldRun;
        },
        ...mapState(useCountdownStore, ["timerShouldRun", "remainingSeconds"])
    },
    methods: {
        formatTime: function (seconds) {
            return ("0" + seconds).slice(-2);
        },
    },
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
        font-weight: 700;
        vertical-align: middle;
    }
}
</style>
