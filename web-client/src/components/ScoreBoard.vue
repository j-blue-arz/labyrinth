<template>
    <div class="score-board">
        <v-score-board-row
            v-for="player in players"
            :key="'score-row-' + player.id"
            :player="player"
            :controller="controller"
        />
    </div>
</template>

<script>
import VScoreBoardRow from "@/components/VScoreBoardRow.vue";

export default {
    name: "score-board",
    components: {
        VScoreBoardRow
    },
    props: {
        players: {
            type: Array,
            required: true
        },
        controller: {
            type: Object,
            required: true
        }
    }
};
</script>

<style lang="scss">
.score-board {
    height: 100%;
    display: flex;
    flex-flow: column wrap;
    align-items: center;
    align-content: center;
    justify-content: start;
}
</style>
