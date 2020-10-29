<template>
    <div class="game-menu">
        <div class="game-menu__button">
            <span @click.self="onToggleMenu" ref="game-menu-button" class="game-menu__button-text"
                >Menu</span
            >
        </div>
        <v-menu
            @item-click="onItemClick($event)"
            :visible="menuIsVisible"
            :menu-items="menuItems"
        />
    </div>
</template>

<script>
import VMenu from "@/components/VMenu.vue";
import MenuItem from "@/model/menuItem.js";
import Player from "@/model/player.js";

const REMOVE_PREFIX = "remove-";
const ADD_PREFIX = "add-";
const RESTART_PREFIX = "restart-";

export default {
    name: "game-menu",
    props: {
        controller: {
            type: Object,
            required: true
        }
    },
    components: {
        VMenu
    },
    data() {
        return {
            menuIsVisible: false
        };
    },
    computed: {
        menuItems: function() {
            let menu = [];
            if (this.playerManager.hasUserPlayer()) {
                menu.push(new MenuItem("leave", "Leave game"));
            } else {
                menu.push(new MenuItem("enter", "Enter game"));
            }
            if (this.players.length < 4) {
                let submenu = [];
                if (this.computationMethods) {
                    this.computationMethods.forEach(method => {
                        let key = ADD_PREFIX + method;
                        let text = Player.computationMethodLabel(method);
                        submenu.push(new MenuItem(key, text));
                    });
                }
                if (this.playerManager.canAddWasmPlayer()) {
                    submenu.push(new MenuItem("add-wasm", "WASM: Exhaustive Search (1P)"));
                }
                menu.push(new MenuItem("add", "Add computer..", submenu));
            }
            if (this.computerPlayers.length > 0 || this.playerManager.hasWasmPlayer()) {
                let submenu = [];
                for (let player of this.computerPlayers) {
                    let key = REMOVE_PREFIX + player.id;
                    let label = player.getLabel();
                    let text = "" + player.colorIndex + " - " + label;
                    submenu.push(new MenuItem(key, text));
                }
                if (this.playerManager.hasWasmPlayer()) {
                    let playerId = this.playerManager.getWasmPlayer();
                    let player = this.controller.getGame().getPlayer(playerId);
                    if (player) {
                        let label = player.getLabel();
                        let text = "" + player.colorIndex + " - " + label;
                        submenu.push(new MenuItem("remove-wasm", text));
                    }
                }
                menu.push(new MenuItem("remove", "Remove computer..", submenu));
            }
            menu.push(
                new MenuItem("restart", "Restart with..", [
                    new MenuItem(RESTART_PREFIX + "7", "original size (7)"),
                    new MenuItem(RESTART_PREFIX + "9", "large size (9)"),
                    new MenuItem(RESTART_PREFIX + "13", "huge size (13)")
                ])
            );
            return menu;
        },
        computerPlayers: function() {
            return this.controller.getGame().getComputerPlayers();
        },
        players: function() {
            return this.controller.getGame().getPlayers();
        },
        playerManager: function() {
            return this.controller.getPlayerManager();
        },
        computationMethods: function() {
            return this.controller.getComputationMethods();
        }
    },
    methods: {
        onToggleMenu: function() {
            this.menuIsVisible = !this.menuIsVisible;
        },
        onItemClick: function($event) {
            this.closeMenu();
            if ($event === "leave") {
                this.controller.leaveGame();
            } else if ($event === "enter") {
                this.controller.enterGame();
            } else if ($event === "add-wasm") {
                this.controller.addWasmPlayer();
            } else if ($event === "remove-wasm") {
                this.controller.removeWasmPlayer();
            } else if ($event.startsWith(ADD_PREFIX)) {
                let computeMethod = $event.substr(ADD_PREFIX.length);
                this.controller.addComputer(computeMethod);
            } else if ($event.startsWith(REMOVE_PREFIX)) {
                let playerId = Number.parseInt($event.substr(REMOVE_PREFIX.length));
                this.controller.removeComputer(playerId);
            } else if ($event.startsWith(RESTART_PREFIX)) {
                let size = Number.parseInt($event.substr(RESTART_PREFIX.length));
                this.controller.restartWithSize(size);
            }
        },
        closeMenu: function() {
            this.menuIsVisible = false;
        }
    }
};
</script>

<style lang="scss">
.game-menu {
    position: relative;

    &__button {
        text-align: center;
        display: table;
        width: 6rem;
        background-color: $color-menu-button;
        height: 4rem;

        &:hover {
            background-color: $color-menu-hover;
        }
    }

    &__button-text {
        display: table-cell;
        vertical-align: middle;
    }
}
</style>
