import Game, { SHIFT_ACTION } from "@/model/game.js";
import MazeCard from "@/model/mazeCard.js";
import Player from "@/model/player.js";

export default class GameFactory {
    constructor(initialPlayerLocations = []) {
        this._initialPlayerLocations = initialPlayerLocations;
        this.nextAction = SHIFT_ACTION;
    }

    createGame() {
        var game = new Game();

        var id = 0;
        for (var row = 0; row < game.n; row++) {
            game.mazeCards.push([]);
            for (var col = 0; col < game.n; col++) {
                game.mazeCards[row].push(MazeCard.createNewRandom(id, row, col));
                id++;
            }
        }

        if (this._initialPlayerLocations.length === 0) {
            this._initialPlayerLocations.push(this._randomLocation(game.n));
        }

        for (var i = 0; i < this._initialPlayerLocations.length; i++) {
            let location = this._initialPlayerLocations[i];
            let playerMazeCard = game.getMazeCard(location);
            let player = new Player(i, i);
            player.mazeCard = playerMazeCard;
            playerMazeCard.addPlayer(player);
            game.addPlayer(player);
        }
        game.getPlayer(0).isUser = true;

        game.getMazeCard(this._randomLocation(game.n)).hasObject = true;

        game.setNextAction({ playerId: 0, action: this.nextAction });

        game.leftoverMazeCard = MazeCard.createNewRandom(id, -1, -1);
        return game;
    }

    _randomLocation(n) {
        return {
            row: Math.floor(Math.random() * n),
            column: Math.floor(Math.random() * n)
        };
    }
}
