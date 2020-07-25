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

const NOT_PARTICIPATING = -1;
const REMOVE_PREFIX = "remove-";
const ADD_PREFIX = "add-";
const RESTART_PREFIX = "restart-";

export default {
    name: "game-menu",
    props: {
        api: {
            required: true
        },
        game: {
            require: true
        },
        userPlayerId: {
            type: Number,
            require: true
        }
    },
    components: {
        VMenu
    },
    watch: {
        computerPlayers: function() {
            this.updateRemoveMenuItems();
        },
        userPlayerId: function() {
            this.updateLeaveEnterMenuItem();
            this.updateReplaceWasmMenuItem();
        }
    },
    data() {
        return {
            menuIsVisible: false,
            menuItems: [
                new MenuItem("leave", "Leave game"),
                new MenuItem("replace-wasm", "Let WASM play for me"),
                new MenuItem("add", "Add computer..", [
                    new MenuItem(ADD_PREFIX + "exhaustive-search", "Exhaustive Search"),
                    new MenuItem(ADD_PREFIX + "minimax", "Minimax"),
                    new MenuItem(ADD_PREFIX + "alpha-beta", "Alpha-Beta"),
                    new MenuItem(ADD_PREFIX + "dynamic-libexhsearch", "Library: libexhsearch")
                ]),
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
            return this.game.getComputerPlayers();
        }
    },
    methods: {
        updateRemoveMenuItems: function() {
            let menuItemRemove = this.menuItems.find(item => item.key === "remove");
            menuItemRemove.submenu = [];
            for (let player of this.computerPlayers) {
                let key = REMOVE_PREFIX + player.id;
                let text = "" + player.colorIndex + " - " + player.computationMethodLabel();
                menuItemRemove.submenu.push(new MenuItem(key, text));
            }
        },
        updateLeaveEnterMenuItem: function() {
            if (this.userPlayerId === NOT_PARTICIPATING) {
                Vue.set(this.menuItems, 0, new MenuItem("enter", "Enter game"));
            } else {
                Vue.set(this.menuItems, 0, new MenuItem("leave", "Leave game"));
            }
        },
        updateReplaceWasmMenuItem: function() {
            var menuItemReplaceIndex = this.menuItems.findIndex(
                item => item.key === "replace-wasm"
            );
            if (menuItemReplaceIndex >= 0 && this.userPlayerId === NOT_PARTICIPATING) {
                this.menuItems.splice(menuItemReplaceIndex, 1);
            } else if (menuItemReplaceIndex === -1 && this.userPlayerId !== NOT_PARTICIPATING) {
                this.menuItems.splice(1, 0, new MenuItem("replace-wasm", "Let WASM play for me"));
            }
        },
        onToggleMenu: function() {
            this.menuIsVisible = !this.menuIsVisible;
        },
        onItemClick: function($event) {
            this.closeMenu();
            if ($event === "leave") {
                this.$emit("leave-game");
            } else if ($event === "enter") {
                this.$emit("enter-game");
            } else if ($event === "replace-wasm") {
                this.$emit("replace-wasm");
            } else if ($event.startsWith(ADD_PREFIX)) {
                let computeMethod = $event.substr(ADD_PREFIX.length);
                this.addComputer(computeMethod);
            } else if ($event.startsWith(REMOVE_PREFIX)) {
                let playerId = Number.parseInt($event.substr(REMOVE_PREFIX.length));
                this.removeComputer(playerId);
            } else if ($event.startsWith(RESTART_PREFIX)) {
                let size = Number.parseInt($event.substr(RESTART_PREFIX.length));
                this.restartWithSize(size);
            }
        },
        closeMenu: function() {
            this.menuIsVisible = false;
        },
        addComputer: function(computeMethod) {
            this.api
                .doAddComputerPlayer(computeMethod)
                .catch(this.handleError)
                .then(this.calledApiMethod);
        },
        removeComputer: function(playerId) {
            this.api
                .removePlayer(playerId)
                .catch(this.handleError)
                .then(this.calledApiMethod);
        },
        restartWithSize: function(size) {
            this.api
                .changeGame(size)
                .catch(this.handleError)
                .then(this.calledApiMethod);
        },
        handleError: function(error) {
            console.error(error);
        },
        calledApiMethod: function() {
            this.$emit("called-api-method");
        }
    },
    mounted() {
        this.updateRemoveMenuItems();
        this.updateLeaveEnterMenuItem();
        this.updateReplaceWasmMenuItem();
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
