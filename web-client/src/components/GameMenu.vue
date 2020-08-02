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
import Vue from "vue";
import VMenu from "@/components/VMenu.vue";
import MenuItem from "@/model/menuItem.js";
import Player from "@/model/player.js";
import Controller from "@/controllers/controller.js";

const REMOVE_PREFIX = "remove-";
const ADD_PREFIX = "add-";
const RESTART_PREFIX = "restart-";

export default {
    name: "game-menu",
    props: {
        controller: {
            type: Controller,
            required: true
        }
    },
    components: {
        VMenu
    },
    watch: {
        computerPlayers: function() {
            this.updateRemoveMenuItems();
        },
        hasUserPlayer: function() {
            this.updateLeaveEnterMenuItem();
        },
        hasWasmPlayer: function() {
            this.updateWasmMenuItem();
            this.updateRemoveMenuItems();
        },
        computationMethods: function() {
            this.updateAddComputerMenuItems();
        }
    },
    data() {
        return {
            menuIsVisible: false,
            menuItems: [
                new MenuItem("leave", "Leave game"),
                new MenuItem("add", "Add computer..", []),
                new MenuItem("remove", "Remove computer..", []),
                new MenuItem("restart", "Restart with..", [
                    new MenuItem(RESTART_PREFIX + "7", "original size (7)"),
                    new MenuItem(RESTART_PREFIX + "9", "large size (9)"),
                    new MenuItem(RESTART_PREFIX + "13", "huge size (13)")
                ])
            ]
        };
    },
    computed: {
        computerPlayers: function() {
            return this.controller.game.getComputerPlayers();
        },
        playerManager: function() {
            return this.controller.playerManager;
        },
        hasUserPlayer: function() {
            return this.playerManager.hasUserPlayer();
        },
        hasWasmPlayer: function() {
            return this.playerManager.hasWasmPlayer();
        },
        computationMethods: function() {
            return this.controller.computationMethods;
        }
    },
    methods: {
        updateAddComputerMenuItems: function() {
            let menuItemAddComputer = this.menuItems.find(item => item.key === "add");
            menuItemAddComputer.submenu = [];
            if (this.computationMethods) {
                this.computationMethods.forEach(method => {
                    let key = ADD_PREFIX + method;
                    let text = Player.computationMethodLabel(method);
                    menuItemAddComputer.submenu.push(new MenuItem(key, text));
                });
            }
            this.updateWasmMenuItem();
        },
        updateWasmMenuItem: function() {
            let addComputerMenu = this.menuItems.find(item => item.key === "add").submenu;
            let index = addComputerMenu.find(item => item.key === "enter-wasm");
            if (this.playerManager.canAddWasmPlayer()) {
                if (index === -1) {
                    addComputerMenu.push(new MenuItem("enter-wasm", "WASM: Exhaustive Search"));
                }
            } else {
                if (index > -1) {
                    addComputerMenu.splice(index, 1);
                }
            }
        },
        updateRemoveMenuItems: function() {
            let menuItemRemove = this.menuItems.find(item => item.key === "remove");
            menuItemRemove.submenu = [];
            for (let player of this.computerPlayers) {
                let key = REMOVE_PREFIX + player.id;
                let label = player.getLabel();
                let text = "" + player.colorIndex + " - " + label;
                menuItemRemove.submenu.push(new MenuItem(key, text));
            }
            if (this.playerManager.hasWasmPlayer()) {
                menuItemRemove.submenu.push(new MenuItem("remove-wasm", "WASM: Exhaustive Search"));
            }
        },
        updateLeaveEnterMenuItem: function() {
            if (this.playerManager.hasUserPlayer()) {
                Vue.set(this.menuItems, 0, new MenuItem("leave", "Leave game"));
            } else {
                Vue.set(this.menuItems, 0, new MenuItem("enter", "Enter game"));
            }
        },
        onToggleMenu: function() {
            this.menuIsVisible = !this.menuIsVisible;
        },
        onItemClick: function($event) {
            this.closeMenu();
            if ($event === "leave") {
                this.controller.leaveGame();
            } else if ($event === "enter") {
                this.controller.enterGame();
            } else if ($event === "wasm") {
                this.controller.addWasmPlayer();
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
    },
    mounted() {
        this.updateRemoveMenuItems();
        this.updateAddComputerMenuItems();
        this.updateLeaveEnterMenuItem();
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
