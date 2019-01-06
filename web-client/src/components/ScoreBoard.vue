<template>
    <table class="score-board">
        <v-score-board-row
            v-for="player in players"
            :key="'score-row-' + player.id"
            :player="player"
        />
    </table>
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
        }
    }
};
</script>

<style lang="scss">
.score-board {
    width: 100px;
    border-collapse: collapse;
    table-layout: fixed;
}
</style>
