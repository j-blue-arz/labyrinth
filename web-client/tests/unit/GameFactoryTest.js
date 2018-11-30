import GameFactory from "@/model/gameFactory";
import { assertConsistentLocation, loc } from "./testutils.js";

describe("GameFactory.createGame()", () => {
    it("creates a game with 7x7 maze cards", () => {
        let game = new GameFactory().createGame();
        expect(game.mazeCards.length).toBe(7);
        for (let i = 0; i < 7; i++) {
            expect(game.mazeCards[i].length).toBe(7);
        }
    });

    it("creates a game with consistent maze card locations.", () => {
        let game = new GameFactory().createGame();
        for (let row = 0; row < 7; row++) {
            for (let column = 0; column < 7; column++) {
                assertConsistentLocation(game, loc(row, column));
            }
        }
    });

    it("creates a game with one player with id 0.", () => {
        let game = new GameFactory().createGame();
        expect(game._players.size).toBe(1);
        expect(game.getPlayer(0)).toBeTruthy();
        expect(game.getPlayer(0).id).toBe(0);
    });

    it("creates a player with consistent maze card", () => {
        let game = new GameFactory().createGame();
        let player = game.getPlayer(0);
        expect(player.mazeCard.players).toEqual([player]);
    });

    it("creates a leftover maze card", () => {
        let game = new GameFactory().createGame();
        let leftoverMazeCard = game.leftoverMazeCard;
        expect(leftoverMazeCard.location).toEqual(loc(-1, -1));
    });

    describe("with three initial locations", () => {
        it("creates three players with consistent consecutive ids", () => {
            let playerLocations = [loc(0, 0), loc(3, 4), loc(2, 5)];
            let game = new GameFactory(playerLocations).createGame();
            expect(game._players.size).toBe(3);
            expect(game.getPlayer(0).id).toBe(0);
            expect(game.getPlayer(1).id).toBe(1);
            expect(game.getPlayer(2).id).toBe(2);
        });

        it("creates three players with consistent maze card", () => {
            let playerLocations = [loc(0, 0), loc(3, 4), loc(2, 5)];
            let game = new GameFactory(playerLocations).createGame();
            for (let id = 0; id < 3; id++) {
                let player = game.getPlayer(id);
                expect(player.mazeCard.players).toEqual([player]);
            }
        });

        it("creates three players with correct locations", () => {
            let playerLocations = [loc(0, 0), loc(3, 4), loc(2, 5)];
            let game = new GameFactory(playerLocations).createGame();
            for (let id = 0; id < 3; id++) {
                let player = game.getPlayer(id);
                expect(player.mazeCard.location).toEqual(playerLocations[id]);
            }
        });
    });

    describe("with three equal initial locations", () => {
        it("placed all players on the same maze card", () => {
            let playerLocations = [loc(0, 0), loc(0, 0), loc(0, 0)];
            let game = new GameFactory(playerLocations).createGame();
            expect(game.getMazeCard(loc(0, 0)).players.length).toBe(3);
        });
    });
});
