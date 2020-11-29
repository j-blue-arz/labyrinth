<template>
    <div class="game-container">
        <interactive-board
            v-if="hasStarted"
            :controller="controller"
            ref="interactive-board"
            class="game-container__main-content"
        />
        <div class="game-container__sidebar">
            <div>
                <timer :controller="controller" />
            </div>
            <div>
                <score-board :players="players" />
            </div>
            <div>
                <game-menu :controller="controller" />
            </div>
        </div>
    </div>
</template>

<script>
import InteractiveBoard from "@/components/InteractiveBoard.vue";
import GameMenu from "@/components/GameMenu.vue";
import ScoreBoard from "@/components/ScoreBoard.vue";
import Timer from "@/components/Timer.vue";
import Controller from "@/controllers/controller.js";

export default {
    name: "game-container",
    components: {
        InteractiveBoard,
        GameMenu,
        ScoreBoard,
        Timer
    },
    data() {
        return {
            controller: null
        };
    },
    computed: {
        players: function() {
            return this.controller.game.getPlayers();
        },
        hasStarted: function() {
            return this.controller && this.controller.game && this.controller.game.hasStarted();
        },
        game: function() {
            return this.controller.game;
        }
    },
    created: function() {
        let useStorage = process.env.NODE_ENV === "production";
        this.controller = new Controller(useStorage);
        window.addEventListener("beforeunload", () => this.controller.beforeDestroy());
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
    justify-content: space-evenly;
    align-items: center;
    align-content: flex-start;

    &__main-content {
        flex: 1 100%;
        order: 1;
    }

    &__sidebar {
        flex-grow: 1;
        order: 2;
        display: flex;
        justify-content: space-evenly;
        align-items: center;

        div {
            flex: 1;
        }
    }
}

@media all and (orientation: landscape) {
    .game-container {
        flex-flow: column wrap;
    }

    .game-container__main-content {
        height: 100%;
    }

    .game-container__sidebar {
        flex-flow: column nowrap;
    }
}

@media all and (orientation: portrait) {
    .game-container {
        flex-flow: row wrap;
    }

    .game-container__main-content {
        width: 100%;
    }

    .game-container__sidebar {
        flex-flow: row nowrap;
    }
}
</style>
