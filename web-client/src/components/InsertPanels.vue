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
import InsertPanel from "@/model/insertPanel.js";

export default {
    name: "insert-panels",
    components: {
        VInsertPanel
    },
    props: {
        game: {
            type: Object,
            required: true
        },
        interaction: {
            type: Boolean,
            required: true
        }
    },
    computed: {
        insertPanels: function() {
            let result = [];
            let id = 0;
            let n = this.game.n;
            let shiftLocations = this.game.getShiftLocations();
            for (let location of shiftLocations) {
                let insertPanel = new InsertPanel(id++, location, n);
                if (this.locationsEqual(this.game.disabledShiftLocation, location)) {
                    insertPanel.enabled = false;
                }
                result.push(insertPanel);
            }
            return result;
        }
    },
    methods: {
        xPos(insertPanel) {
            return this.$ui.cardSize * insertPanel.displayLocation.column + this.$ui.boardOffset;
        },
        yPos(insertPanel) {
            return this.$ui.cardSize * insertPanel.displayLocation.row + this.$ui.boardOffset;
        },
        locationsEqual(locA, locB) {
            return locA && locB && locA.row === locB.row && locA.column === locB.column;
        },
        onClick: function(event, insertPanel) {
            if (this.interaction && insertPanel.enabled) {
                this.$emit("insert-panel-clicked", insertPanel.shiftLocation);
            }
        }
    }
};
</script>
