<template>
    <g>
        <v-insert-panel
            v-for="insertPanel in insertPanels"
            @panel-click="onClick($event, insertPanel)"
            :key="'panel-' + insertPanel.id"
            :insert-panel="insertPanel"
            :x-pos="xPos(insertPanel)"
            :y-pos="yPos(insertPanel)"
            :size="$ui.cardSize"
            :interaction="interaction"
        />
    </g>
</template>

<script>
import VInsertPanel from "@/components/VInsertPanel.vue";
import { InsertPanel } from "@/model/shift.js";
import { locationsEqual, getShiftLocations } from "@/store/modules/board.js";
import { SHIFT_ACTION } from "@/model/player.js";

export default {
    name: "insert-panels",
    components: {
        VInsertPanel,
    },
    emits: ["player-shift"],
    computed: {
        insertPanels: function () {
            let result = [];
            let id = 0;
            const mazeSize = this.$store.state.board.mazeSize;
            let shiftLocations = getShiftLocations(mazeSize);
            for (let location of shiftLocations) {
                let insertPanel = new InsertPanel(id++, location, mazeSize);
                if (locationsEqual(this.$store.state.board.disabledShiftLocation, location)) {
                    insertPanel.enabled = false;
                }
                result.push(insertPanel);
            }
            return result;
        },
        interaction: function () {
            return this.$store.getters["players/userPlayer"]?.nextAction === SHIFT_ACTION;
        },
    },
    methods: {
        xPos(insertPanel) {
            return this.$ui.cardSize * insertPanel.displayLocation.column;
        },
        yPos(insertPanel) {
            return this.$ui.cardSize * insertPanel.displayLocation.row;
        },
        onClick: function (event, insertPanel) {
            if (this.interaction && insertPanel.enabled) {
                this.$emit("player-shift", insertPanel.shiftLocation);
            }
        },
    },
};
</script>
