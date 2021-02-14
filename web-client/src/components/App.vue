<template>
    <div class="app">
        <v-menu-bar class="app__menubar" :controller="controller" />
        <div class="app__game">
            <div class="game__board">
                <interactive-board
                    v-if="hasStarted"
                    :controller="controller"
                    ref="interactive-board"
                />
            </div>
            <timer
                class="game__timer"
                :controller="controller"
                :countdown="countdown"
                :user-player="userPlayer"
            />
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
import VMenuBar from "@/components/VMenuBar.vue";
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
    font-family: Helvetica, sans-serif;
}

*,
::after,
::before {
    box-sizing: inherit;
    padding: 0;
    margin: 0;
}

html {
    box-sizing: border-box;
}

body {
    height: 100vh;
    width: 100vw;
    margin: 0;
    color: $text-color;
    background: $color-background;
    overflow: hidden;
}

.app {
    height: 100%;
    width: 100%;

    &__game {
        z-index: 0;
        height: 100%;
        width: 100%;
        display: grid;
        grid-template-columns: 1fr minmax(70vmin, 100vh) 1fr;
        grid-template-rows: 1fr 4rem 4 * $score-row-height 8rem 1fr;
        grid-template-areas:
            ". board . "
            ". board timer"
            ". board score"
            ". board message"
            ". board .";
        grid-gap: 2vmin;
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
        @include game-widget;
    }

    &__score {
        grid-area: score;
        @include game-widget;
    }

    &__message {
        grid-area: message;
    }
}

html {
    font-size: 12px;

    @media only screen and (min-width: 1200px) {
        font-size: 16px;
    }

    @media only screen and (min-width: 320px) {
        font-size: calc(12px + 4 * (100vw - 320px) / 880);
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
