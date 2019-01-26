<template>
    <div class="game-menu">
        <div class="game-menu__button">
            <span @click.self="onOpenMenu" class="game-menu__button-text">Menu</span>
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
        onOpenMenu: function() {
            this.menuIsVisible = true;
            //this.menuIsVisible = true;
        },
        onItemClick: function($event) {
            this.closeMenu();
            if ($event === "remove") {
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
