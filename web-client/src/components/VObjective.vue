<template>
    <svg :height="$ui.cardSize" :width="$ui.cardSize" viewBox="-50 -50 100 100">
        <g class="objective">
            <line
                :x1="svgFlagLine.x"
                :y1="-svgFlagLine.y"
                :x2="svgFlagLine.x"
                :y2="svgFlagLine.y"
            />
            <polygon :points="svgFlagPolygon"></polygon>
        </g>
    </svg>
</template>
<script>
export default {
    name: "v-objective",
    data() {
        return {
            mastSize: 50,
            flagLength: 26,
            flagX: -4,
        };
    },
    computed: {
        svgFlagLine: function () {
            return this.flagTop();
        },
        svgFlagPolygon: function () {
            return [this.flagTop(), this.flagPoint(), this.flagBase()]
                .map(this.toString)
                .join(", ");
        },
    },
    methods: {
        toString(point) {
            return point.x + "," + point.y;
        },
        mastTop() {
            return { x: this.flagX, y: -this.mastSize / 2 };
        },
        flagTop() {
            return this.mastTop();
        },
        flagPoint() {
            return { x: this.flagX + this.flagLength, y: -this.mastSize / 4 };
        },
        flagBase() {
            return { x: this.flagX, y: 0 };
        },
        mastFoot() {
            return { x: this.flagX, y: this.mastSize / 2 };
        },
    },
};
</script>

<style lang="scss">
.objective {
    stroke: $objective-color;
    fill: $objective-color;

    line {
        stroke-width: 2px;
    }
}
</style>
