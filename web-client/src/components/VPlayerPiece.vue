<template>
    <circle
        ref="playerPiece"
        :cx="xCenterPos"
        :cy="yCenterPos"
        :r="maxSize/2"
        :class="`player-piece player-piece__player-${playerIndex}`"/>
</template>

<script>
export default {
    name: "v-player-piece",
    props: {
        playerIndex: {
            type: Number,
            require: true
        },
        xCenterPos: {
            type: Number,
            require: true
        },
        yCenterPos: {
            type: Number,
            require: true
        },
        maxSize: {
            type: Number,
            require: true
        }
    }
};
</script>

<style lang="scss">
.player-piece {
    stroke: black;
    stroke-width: 3px;

    &__player-0 {
        fill: #274594;
    }

    &__player-1 {
        fill: #931717;
    }

    &__player-2 {
        fill: #efb520;
    }

    &__player-3 {
        fill: #50a28c;
    }
}
</style>
