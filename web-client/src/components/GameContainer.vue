<template>
    <div class="game-container">
        <interactive-board
            :controller="controller"
            ref="interactive-board"
            class="game-container__main-content"
        />
        <score-board :players="players" class="game-container__score" />
        <game-menu :controller="controller" class="game-container__menu" />
    </div>
</template>

<script>
import InteractiveBoard from "@/components/InteractiveBoard.vue";
import GameMenu from "@/components/GameMenu.vue";
import ScoreBoard from "@/components/ScoreBoard.vue";
import Controller from "@/controllers/controller.js";

export default {
    name: "game-container",
    components: {
        InteractiveBoard,
        GameMenu,
        ScoreBoard
    },
    data() {
        return {
            controller: null
        };
    },
    computed: {
        players: function() {
            return this.controller.game.getPlayers();
        }
    },
    created: function() {
        let useStorage = process.env.NODE_ENV === "production";
        this.controller = new Controller(useStorage);
        this.controller.initialize();
    },
    beforeDestroy() {
        this.controller.beforeDestroy();
    }
};
</script>

<style lang="scss">
.game-container {
    box-sizing: border-box;
    width: 100%;
    height: 100%;
    display: flex;
    position: relative;
    justify-content: space-around;
    align-items: flex-start;
    align-content: flex-start;

    &__main-content {
        flex: 1 100%;
        order: 1;
    }

    &__score {
        order: 2;
    }

    &__menu {
        order: 3;
    }
}

@media all and (orientation: landscape) {
    .game-container {
        flex-flow: column wrap;
    }

    .game-container__main-content {
        height: 100%;
    }
}

@media all and (orientation: portrait) {
    .game-container {
        flex-flow: row wrap;
    }

    .game-container__main-content {
        width: 100%;
    }
}
</style>
