<template>
    <div class="timer" :class="{ 'timer--invisible': !visible }">
        0<span class="timer__separator">:</span>{{ formatTime(remainingSeconds) }}
    </div>
</template>

<script>
export default {
    name: "countdown-timer",
    computed: {
        remainingSeconds: function () {
            return this.$store.state.countdown.remainingSeconds;
        },
        visible: function () {
            return this.$store.getters["countdown/timerShouldRun"];
        },
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
