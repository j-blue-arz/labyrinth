<template>
    <v-menu @item-click="onItemClick($event)" :menu-items="menuItems" />
</template>

<script>
import VMenu from "@/components/VMenu.vue";
import MenuItem from "@/model/menuItem.js";
import { getLabel, computationMethodLabel } from "@/model/player.js";
import API from "@/services/game-api.js";

import { mapStores } from 'pinia';
import { useGameStore } from '@/stores/game.js';
import { usePlayersStore } from '@/stores/players.js';

const REMOVE_PREFIX = "remove-";
const ADD_PREFIX = "add-";
const RESTART_PREFIX = "restart-";

export default {
    name: "game-menu",
    components: {
        VMenu,
    },
    emits: ["item-click"],
    computed: {
        menuItems: function () {
            let menu = [];
            if (this.playersStore.hasUserPlayer) {
                menu.push(new MenuItem("leave", "Leave game"));
            } else {
                menu.push(new MenuItem("enter", "Enter game"));
            }
            if (this.gameIsNotFull) {
                let submenu = this.createAddBotSubmenu();
                if (submenu.length > 0) {
                    menu.push(new MenuItem("add", "Add bot..", submenu));
                }
            }
            let submenu = this.removeBotSubmenu();
            if (submenu.length > 0) {
                menu.push(new MenuItem("remove", "Remove bot..", submenu));
            }
            menu.push(
                new MenuItem("restart", "Restart with..", [
                    new MenuItem(RESTART_PREFIX + "7", "original size (7)"),
                    new MenuItem(RESTART_PREFIX + "9", "large size (9)"),
                    new MenuItem(RESTART_PREFIX + "13", "huge size (13)"),
                ])
            );
            if (this.gameStore.isOffline) {
                menu.push(new MenuItem("connect", "Connect to server"));
            } else {
                menu.push(new MenuItem("disconnect", "Disconnect"));
            }
            return menu;
        },
        bots: function () {
            return this.playersStore.bots;
        },
        gameIsNotFull: function () {
            return this.playersStore.allIds.length < 4;
        },
        ...mapStores(useGameStore, usePlayersStore)
    },
    methods: {
        onItemClick: function ($event) {
            if ($event === "leave") {
                this.playersStore.leaveGame();
            } else if ($event === "enter") {
                this.playersStore.enterGame();
            } else if ($event === "connect") {
                this.gameStore.playOnline();
            } else if ($event === "disconnect") {
                this.gameStore.playOffline();
            } else if ($event === "add-wasm") {
                this.playersStore.addWasmPlayer();
            } else if ($event === "remove-wasm") {
                this.playersStore.removeWasmPlayer();
            } else if ($event.startsWith(ADD_PREFIX)) {
                let computeMethod = $event.substr(ADD_PREFIX.length);
                API.doAddBot(computeMethod);
            } else if ($event.startsWith(REMOVE_PREFIX)) {
                let playerId = Number.parseInt($event.substr(REMOVE_PREFIX.length));
                API.removePlayer(playerId);
            } else if ($event.startsWith(RESTART_PREFIX)) {
                let size = Number.parseInt($event.substr(RESTART_PREFIX.length));
                if (this.gameStore.isOnline) {
                    API.changeGame(size);
                } else {
                    this.gameStore.playOffline(size);
                }
            }
            this.$emit("item-click");
        },
        createAddBotSubmenu: function () {
            let submenu = [];
            const computationMethods = this.gameStore.computationMethods;
            if (computationMethods) {
                computationMethods.forEach((method) => {
                    let key = ADD_PREFIX + method;
                    let text = computationMethodLabel(method);
                    submenu.push(new MenuItem(key, text));
                });
            }
            return submenu;
        },
        removeBotSubmenu: function () {
            let submenu = [];
            for (let player of this.bots) {
                let key = REMOVE_PREFIX + player.id;
                let label = getLabel(player);
                let text = "" + player.pieceIndex + " - " + label;
                submenu.push(new MenuItem(key, text));
            }
            if (this.playersStore.hasWasmPlayer) {
                let playerId = this.playersStore.wasmPlayerId;
                let player = this.playersStore.find(playerId);
                if (player) {
                    let label = getLabel(player);
                    let text = "" + player.pieceIndex + " - " + label;
                    submenu.push(new MenuItem("remove-wasm", text));
                }
            }
            return submenu;
        },
    },
};
</script>

<style lang="scss"></style>
