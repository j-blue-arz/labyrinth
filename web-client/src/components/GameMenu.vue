<template>
    <div @click="onOpenMenu" class="game-menu game-menu__button">
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
    data() {
        return {
            menuIsVisible: false,
            menuItems: [
                new MenuItem("close", "Close menu"),
                new MenuItem("remove", "Remove computers"),
                new MenuItem("exhaustive-search", "Replace by exhaustive search"),
                new MenuItem("minimax", "Replace by Minimax"),
                new MenuItem("alpha-beta", "Replace by Alpha-Beta")
            ]
        };
    },
    methods: {
        onOpenMenu: function(event) {
            if (event.ctrlKey) {
                this.menuIsVisible = true;
            }
        },
        onItemClick: function($event) {
            if ($event === "close") {
                this.closeMenu();
            } else if ($event === "remove") {
                this.removeComputers();
            } else if ($event === "exhaustive-search") {
                this.replaceByComputer("exhaustive-search");
            } else if ($event === "minimax") {
                this.replaceByComputer("minimax");
            } else if ($event === "alpha-beta") {
                this.replaceByComputer("alpha-beta");
            }
        },
        removeComputers: function() {
            this.menuIsVisible = false;
            let computerPlayers = this.game.getComputerPlayers();
            let computerPlayerIds = computerPlayers.map(player => player.id);
            this.api
                .removePlayers(computerPlayerIds)
                .catch(this.handleError)
                .then(this.calledApiMethod);
        },
        replaceByComputer: function(type) {
            this.menuIsVisible = false;
            this.api
                .replacePlayer(this.userPlayerId, type)
                .catch(this.handleError)
                .then(this.calledApiMethod);
        },
        closeMenu: function() {
            this.menuIsVisible = false;
        },
        handleError: function(error) {
            console.error(error);
        },
        calledApiMethod: function() {
            this.$emit("called-api-method");
        }
    }
};
</script>

<style lang="scss">
.game-menu__button {
    display: block;
    height: 50px;
    width: 50px;
    background-color: lightgray;
}
</style>
