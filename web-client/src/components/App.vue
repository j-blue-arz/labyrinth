<template>
    <div class="app">
        <div class="app__menubar">
            <v-menu-bar :controller="controller" />
        </div>
        <div class="app__game">
            <div class="game__board">
                <interactive-board
                    v-if="hasStarted"
                    :controller="controller"
                    ref="interactive-board"
                />
            </div>
            <div class="game__timer">
                <timer :controller="controller" :countdown="countdown" :user-player="userPlayer" />
            </div>
            <div class="game__score">
                <score-board :players="players" />
            </div>
            <div class="game__message">
                <v-message-area :countdown="countdown" :user-player="userPlayer" />
            </div>
        </div>
    </div>
</template>

<script>
import InteractiveBoard from "@/components/InteractiveBoard.vue";
import VMenuBar from "@/components/GameMenu.vue";
import ScoreBoard from "@/components/ScoreBoard.vue";
import Timer from "@/components/Timer.vue";
import VMessageArea from "@/components/VMessageArea.vue";
import Controller from "@/controllers/controller.js";
import * as action from "@/model/player.js";

export default {
    name: "app",
    components: {
        InteractiveBoard,
        VMenuBar,
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

*,
::after,
::before {
    box-sizing: inherit;
}

html {
    box-sizing: border-box;
}

body {
    height: 100vh;
    width: 100vw;
    margin: 0;
}

.app {
    height: 100%;
    display: grid;
    grid-template-columns: $menubar-width 1fr;
    grid-template-areas: "menubar game";
    grid-gap: 2vmin;

    &__game {
        grid-area: game;
        display: grid;
        grid-template-columns: 1fr minmax(70vmin, 100vh) 1fr $menubar-width;
        grid-template-rows: 1fr auto 4 * $score-row-height 230px 1fr;
        grid-template-areas:
            ". board . ."
            ". board timer timer"
            ". board score score"
            ". board message message"
            ". board . .";
        grid-gap: 2vmin;
    }

    &__menubar {
        grid-area: menubar;

        @include panel;
    }
}

.game {
    &__board {
        grid-area: board;
        position: relative;
        display: block;
        height: 0;
        padding-bottom: 100%;
        width: 100%;
    }

    &__timer {
        grid-area: timer;
    }

    &__score {
        grid-area: score;
    }

    &__message {
        grid-area: message;
    }
}

/*@media all and (orientation: landscape) {
    .game__board {
        height: 100%;
    }
}

@media all and (orientation: portrait) {
    .game__board {
        width: 100%;
    }
}*/
</style>
