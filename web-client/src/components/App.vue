<template>
    <div class="app">
        <interactive-board
            v-if="hasStarted"
            :controller="controller"
            ref="interactive-board"
            class="app__main-content"
        />
        <div class="app__sidebar">
            <div>
                <timer :controller="controller" :countdown="countdown" :user-player="userPlayer" />
            </div>
            <div>
                <score-board :players="players" />
            </div>
            <div>
                <game-menu :controller="controller" />
            </div>
            <div>
                <v-message-area :countdown="countdown" :user-player="userPlayer" />
            </div>
        </div>
    </div>
</template>

<script>
import InteractiveBoard from "@/components/InteractiveBoard.vue";
import GameMenu from "@/components/GameMenu.vue";
import ScoreBoard from "@/components/ScoreBoard.vue";
import Timer from "@/components/Timer.vue";
import VMessageArea from "@/components/VMessageArea.vue";
import Controller from "@/controllers/controller.js";
import * as action from "@/model/player.js";

export default {
    name: "app",
    components: {
        InteractiveBoard,
        GameMenu,
        ScoreBoard,
        Timer,
        VMessageArea
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
        },
        userPlayer: function() {
            let userPlayerId = this.controller.playerManager.getUserPlayerId();
            let player = this.controller.game.getPlayer(userPlayerId);
            return player;
        },
        countdown: function() {
            return this.controller.turnCountdown;
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
* {
    font-family: Cambria, serif;
}

body {
    height: 100vh;
    width: 100vw;
    margin: 0;
}

.app {
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
    .app {
        flex-flow: column wrap;
    }

    .app__main-content {
        height: 100%;
    }

    .app__sidebar {
        flex-flow: column nowrap;
    }
}

@media all and (orientation: portrait) {
    .app {
        flex-flow: row wrap;
    }

    .app__main-content {
        width: 100%;
    }

    .app__sidebar {
        flex-flow: row nowrap;
    }
}
</style>
