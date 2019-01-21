<template>
    <div @dblclick="onOpenMenu" class="game-menu game-menu__button">
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
                new MenuItem("exhaustive", "Replace by exhaustive search"),
                new MenuItem("minimax", "Replace by minimax"),
                new MenuItem("heuristic", "Replace by heuristic")
            ]
        };
    },
    methods: {
        onOpenMenu: function() {
            this.menuIsVisible = true;
        },
        onItemClick: function($event) {
            if ($event === "close") {
                this.closeMenu();
            } else if ($event === "remove") {
                this.removeComputers();
            } else if ($event === "exhaustive") {
                this.replaceByExhaustive();
            } else if ($event === "minimax") {
                this.replaceByMinimax();
            } else if ($event === "heuristic") {
                this.replaceByHeuristic();
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
        replaceByExhaustive: function() {
            this.replaceByComputer("exhaustive-single");
        },
        replaceByMinimax: function() {
            this.replaceByComputer("minimax");
        },
        replaceByHeuristic: function() {
            this.replaceByComputer("minimax-heuristic");
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
    height: 100px;
    width: 100px;
    background-color: lightblue;
}
</style>
