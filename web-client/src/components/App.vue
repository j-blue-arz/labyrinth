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
import WasmPlayer from "@/model/wasmPlayer.js";

export default {
    name: "app",
    components: {
        VMenuBar,
        VGame
    },
    data() {
        return {
            wasmPlayer: null
        };
    },
    created: function() {
        this.wasmPlayer = new WasmPlayer(this.$store);
        window.addEventListener("beforeunload", () => this.leave());

        this.$store.dispatch("game/playOffline");
    },
    methods: {
        leave() {
            this.$store.dispatch("game/leaveOnlineGame");
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
