<template>
    <svg
    :height="leftoverSize"
    :width="leftoverSize"
    :viewBox="`0 0 160 160`"
    class="leftover">
        <path
            d="M 10 80 A 70 70 0 0 1 80 10 M 73 3 L 80 10 L 73 17"
            class="leftover__interaction-arrow"
            :class="{'leftover__interaction-arrow--interaction': interaction}"
        />
        <v-maze-card
            @click.native="onLeftoverClick"
            v-if="hasStarted"
            :maze-card="mazeCard"
            :card-size="cardSize"
            :x="30"
            :y="30"
            :interaction="interaction"
            class="leftover__card"
            ref="leftover"
        ></v-maze-card>
    </svg>
</template>

<script>
import VMazeCard from "@/components/VMazeCard.vue";
import MazeCard from "@/model/mazeCard.js";

export default {
    name: "leftover-maze-card",
    components: {
        /* eslint-disable vue/no-unused-components */
        VMazeCard
    },
    props: {
        mazeCard: {
            type: MazeCard,
            required: true
        },
        cardSize: {
            type: Number,
            required: true
        },
        interaction: {
            type: Boolean,
            required: false,
            default: false
        }
    },
    computed: {
        hasStarted: function() {
            return this.mazeCard instanceof MazeCard;
        },
        leftoverSize: function() {
            return this.cardSize * 1.6;
        }
    },
    methods: {
        onLeftoverClick: function() {
            if (this.interaction) {
                this.mazeCard.rotateClockwise();
            }
        }
    }
};
</script>

<style lang="scss">
.leftover {
    &__card {
        overflow: visible;
    }

    &__interaction-arrow {
        fill: none;
        stroke: $interaction-color;
        stroke-width: 10;
        stroke-linejoin: round;
        stroke-linecap: round;
        transition: stroke 0.3s;

        &:not(&--interaction) {
            stroke: $interaction-color-secondary;
        }

        &--interaction {
            filter: url(#drop-shadow);
        }
    }
}
</style>
