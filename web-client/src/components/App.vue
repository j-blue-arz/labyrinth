<template>
    <div class="app">
        <v-menu-bar class="app__menubar" />
        <div class="app__main">
            <v-game class="app__game" />
        </div>
    </div>
</template>

<script>
import VMenuBar from "@/components/VMenuBar.vue";
import VGame from "@/components/VGame.vue";
import API from "@/services/game-api.js";

export default {
    name: "app",
    components: {
        VMenuBar,
        VGame
    },
    created: function() {
        API.errorHandlers.push(error => this.handleError(error));
        API.stateObservers.push(apiState => this.$store.dispatch("game/update", apiState));
        API.activatePolling();
        window.addEventListener("beforeunload", () => this.leave());
        this.$store.dispatch("players/enterGame");
    },
    methods: {
        leave() {
            API.stopPolling();
            this.$store.dispatch("players/removeAllClientPlayers");
        },
        handleError(error) {
            if (error.response) {
                if (error.response.data.key === "GAME_NOT_FOUND") {
                    console.log("Game not found, resetting.");
                    this.$store.dispatch("game/reset");
                    API.stopPolling();
                } else {
                    console.error("Response error", error.response.data);
                }
            } else if (error.request) {
                API.stopPolling();
                console.error("Request error", error.request);
            } else {
                console.error("Error", error.message);
            }
        }
    },
    beforeDestroy() {
        this.leave();
    }
};
</script>

<style lang="scss">
* {
    font-family: "Play", Helvetica, sans-serif;
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

input {
    font-family: inherit;
    font-size: inherit;
}

.app {
    height: 100%;

    &__main {
        height: 100%;
        display: grid;

        @media (orientation: landscape) {
            grid-template-columns: 1vmin 1fr auto 1fr 1vmin;
            grid-template-areas: ". . game . .";
        }

        @media (orientation: portrait) {
            grid-template-columns: 1vmin 1fr 1vmin;
            grid-template-rows: 1vmin 1fr 1vmin;
            grid-template-areas: ". . . " ". game ." ". . .";
        }
    }

    &__game {
        grid-area: game;
        height: 100%;
    }
}

html {
    font-size: 11px;

    @media (min-width: 320px) {
        font-size: calc(11px + (100vw - 320px) / 40);
    }

    @media (min-width: 360px) {
        font-size: calc(12px + 4 * (100vw - 360px) / 840);
    }

    @media (min-width: 1200px) {
        font-size: 16px;
    }
}
</style>
