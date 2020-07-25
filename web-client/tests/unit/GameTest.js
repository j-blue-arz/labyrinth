import Game, { loc } from "@/model/game";
import MazeCard from "@/model/mazeCard";
import Player from "@/model/player";
import ValueError from "@/util/exceptions";
import { assertConsistentLocation } from "./testutils.js";

describe("Game", () => {
    describe(".mazeCardsAsList()", () => {
        it("returns 1d-array which contains all the game's maze cards in row-first order", () => {
            let game = new Game();
            game.n = 3;

            let expectedMazeCards = _buildMazeCardMatrix(game);

            let mazeCardList = game.mazeCardsAsList();
            expect(mazeCardList.length).toBe(expectedMazeCards.length);
            for (let i = 0; i < expectedMazeCards.length; i++) {
                expect(mazeCardList).toContain(expectedMazeCards[i]);
            }
        });

        it("returns empty array for empty game.", () => {
            let game = new Game();
            let mazeCardList = game.mazeCardsAsList();
            expect(mazeCardList).toBeInstanceOf(Array);
            expect(mazeCardList.length).toBe(0);
        });

        it("returns 1d-array with the game's maze cards ordered by row, then by column", () => {
            let game = new Game();
            game.n = 7;

            _buildMazeCardMatrix(game);

            let mazeCardList = game.mazeCardsAsList();
            expect(mazeCardList.length).toBe(49);
            let index = 0;
            for (var row = 0; row < game.n; row++) {
                for (var col = 0; col < game.n; col++) {
                    expect(mazeCardList[index]).toBe(game.getMazeCard(loc(row, col)));
                    index++;
                }
            }
        });
    });

    describe(".mazeCardById()", () => {
        it("returns correct maze card for given ID.", () => {
            let game = new Game();
            game.n = 3;
            let mazeCards = _buildMazeCardMatrix(game);
            let expectedMazeCard = mazeCards[1];

            expect(game.mazeCardById(expectedMazeCard.id)).toBe(expectedMazeCard);
        });

        it("returns leftover card if given ID matches", () => {
            let game = new Game();
            game.n = 3;
            let nextId = _maxId(_buildMazeCardMatrix(game)) + 1;
            game.leftoverMazeCard = MazeCard.createNewRandom(nextId, -1, -1);
            let leftover_card_id = game.leftoverMazeCard.id;

            expect(game.mazeCardById(leftover_card_id)).toBe(game.leftoverMazeCard);
        });

        it("returns null for ID which is not in the game.", () => {
            let game = new Game();
            expect(game.mazeCardById(0)).toBeNull();
        });
    });

    describe(".getMazeCard()", () => {
        it("returns the card set by .setMazeCard()", () => {
            let game = new Game();
            game.n = 3;
            let nextId = _maxId(_buildMazeCardMatrix(game)) + 1;
            let mazeCard = MazeCard.createNewRandom(nextId, -1, -1);
            let location = loc(0, 0);
            game.setMazeCard(location, mazeCard);
            expect(game.getMazeCard(location)).toBe(mazeCard);
        });

        it("throws RangeError on invalid location", () => {
            let game = new Game();
            game.n = 3;
            _buildMazeCardMatrix(game);
            let invalidLocation = loc(3, 0);
            expect(() => game.getMazeCard(invalidLocation)).toThrow(RangeError);
        });
    });

    describe(".setMazeCard()", () => {
        it("throws RangeError on invalid location", () => {
            let game = new Game();
            game.n = 3;
            let nextId = _maxId(_buildMazeCardMatrix(game)) + 1;
            let mazeCard = MazeCard.createNewRandom(nextId, -1, -1);
            let invalidLocation = loc(3, 0);
            expect(() => game.setMazeCard(invalidLocation, mazeCard)).toThrow(RangeError);
        });
    });

    describe(".shift()", () => {
        it("shifts correctly on valid location.", () => {
            let game = new Game();
            game.n = 3;
            let nextId = _maxId(_buildMazeCardMatrix(game)) + 1;
            game.leftoverMazeCard = MazeCard.createNewRandom(nextId, -1, -1);
            let oldMatrix = _copyMazeCardMatrix(game);
            let oldLeftOver = game.leftoverMazeCard;

            game.shift(loc(1, 0));

            expect(game.leftoverMazeCard).toBe(oldMatrix[1][2]);
            expect(game.getMazeCard(loc(1, 0))).toBe(oldLeftOver);
            expect(game.getMazeCard(loc(1, 1))).toBe(oldMatrix[1][0]);
            expect(game.getMazeCard(loc(1, 0)).location).toEqual(loc(1, 0));
            expect(game.getMazeCard(loc(1, 2))).toBe(oldMatrix[1][1]);
            expect(game.getMazeCard(loc(1, 0)).location).toEqual(loc(1, 0));

            assertConsistentLocation(game, loc(1, 0));
            assertConsistentLocation(game, loc(1, 1));
            assertConsistentLocation(game, loc(1, 2));
        });

        it("transfers players to pushed-in card.", () => {
            let game = new Game();
            game.n = 3;
            let nextId = _maxId(_buildMazeCardMatrix(game)) + 1;
            game.leftoverMazeCard = MazeCard.createNewRandom(nextId, -1, -1);
            let pushedInCard = game.leftoverMazeCard;
            let player1 = _addPlayer(game, loc(1, 2), 1);
            let player2 = _addPlayer(game, loc(1, 2), 2);

            game.shift(loc(1, 0));

            expect(player1.mazeCard).toBe(pushedInCard);
            expect(player2.mazeCard).toBe(pushedInCard);
            expect(pushedInCard.players.length).toBe(2);
            expect(pushedInCard.players).toEqual(expect.arrayContaining([player1, player2]));
        });

        it("throws ValueError on board location which is not on the border.", () => {
            let game = new Game();
            game.n = 3;
            let nextId = _maxId(_buildMazeCardMatrix(game)) + 1;
            game.leftoverMazeCard = MazeCard.createNewRandom(nextId, -1, -1);

            expect(() => game.shift(loc(1, 1))).toThrow(ValueError);
        });

        it("throws RangeError on invalid shift location.", () => {
            let game = new Game();
            game.n = 3;
            let nextId = _maxId(_buildMazeCardMatrix(game)) + 1;
            game.leftoverMazeCard = MazeCard.createNewRandom(nextId, -1, -1);

            expect(() => game.shift(loc(-1, 3))).toThrow(RangeError);
        });
    });

    describe(".getPlayer()", () => {
        it("returns previously added player.", () => {
            let game = new Game();
            _buildMazeCardMatrix(game);
            let player = _addPlayer(game, loc(1, 1), 7);
            expect(game.getPlayer(7)).toBe(player);
        });

        it(" throws ValueError for not added player.", () => {
            let game = new Game();
            expect(() => game.getPlayer(7)).toThrow(ValueError);
        });
    });

    describe(".getComputerPlayers()", () => {
        it("returns all computer players.", () => {
            let game = new Game();
            _buildMazeCardMatrix(game);
            _addPlayer(game, loc(1, 1), 7);
            let player1 = _addPlayer(game, loc(1, 1), 42);
            player1.isComputer = true;
            let player2 = _addPlayer(game, loc(1, 1), 99);
            player2.isComputer = true;
            let expected = [player1, player2];

            let computerPlayers = game.getComputerPlayers();

            expect(computerPlayers).toEqual(expect.arrayContaining(expected));
            expect(computerPlayers.length).toBe(2);
        });
    });

    describe(".move()", () => {
        it("moves player to correct location.", () => {
            let game = new Game();
            game.n = 3;
            _buildMazeCardMatrix(game);
            let originLocation = loc(0, 0);
            let player = _addPlayer(game, originLocation, 42);
            let originMazeCard = game.getMazeCard(originLocation);
            let targetMazeCard = game.getMazeCard(loc(2, 2));

            game.move(42, loc(2, 2));

            expect(originMazeCard.players.length).toBe(0);
            expect(targetMazeCard.players.length).toBe(1);
            expect(targetMazeCard.players[0]).toBe(player);
            expect(game.getPlayer(42).mazeCard).toBe(targetMazeCard);
        });

        it("throws RangeError on invalid location.", () => {
            let game = new Game();
            game.n = 3;
            _buildMazeCardMatrix(game);
            _addPlayer(game, loc(0, 0), 42);

            expect(() => game.move(42, loc(-1, 2))).toThrow(RangeError);
        });

        it("throws ValueError on invalid playerId.", () => {
            let game = new Game();
            game.n = 3;
            _buildMazeCardMatrix(game);
            _addPlayer(game, loc(0, 0), 42);

            expect(() => game.move(17, loc(1, 1))).toThrow(ValueError);
        });
    });

    describe(".getOppositeLocation()", () => {
        it("returns opposing location for top shift location", () => {
            let game = new Game();
            game.n = 7;

            let result = game.getOppositeLocation(loc(0, 3));
            expect(result).toEqual(loc(6, 3));
        });
    });

    describe(".createFromApi()", () => {
        it("sets maze size correctly", () => {
            let game = new Game();
            game.createFromApi(JSON.parse(GET_STATE_RESULT_FOR_N_3));

            expect(game.n).toEqual(3);
        });

        it("results in a game with two players.", () => {
            let game = new Game();
            game.createFromApi(JSON.parse(GET_STATE_RESULT_FOR_N_3));

            expect(game.getPlayer(42)).not.toBeNull();
            expect(game.getPlayer(17)).not.toBeNull();
        });

        it("places players on correct location.", () => {
            let game = new Game();
            game.createFromApi(JSON.parse(GET_STATE_RESULT_FOR_N_3));

            _assertPlayerLocation(game, 42, loc(2, 2), 16);
            _assertPlayerLocation(game, 17, loc(2, 1), 15);
        });

        it("creates maze card locations consistently.", () => {
            let game = new Game();
            game.createFromApi(JSON.parse(GET_STATE_RESULT_FOR_N_3));

            for (let row = 0; row < game.n; row++) {
                for (let col = 0; col < game.n; col++) {
                    expect(game.getMazeCard(loc(row, col)).location).toEqual(loc(row, col));
                }
            }
        });

        it("creates at least one maze card correctly", () => {
            /* { "outPaths": "NE", "id": 7,  "location": { "column": 0, "row": 1 }, "rotation": 180 } */
            let game = new Game();
            game.createFromApi(JSON.parse(GET_STATE_RESULT_FOR_N_3));

            let mazeCard = game.getMazeCard(loc(1, 0));
            expect(mazeCard.outPaths).toEqual("NE");
            expect(mazeCard.id).toBe(7);
            expect(mazeCard.rotation).toBe(180);
        });

        it("creates leftover maze card correctly", () => {
            /* { "outPaths": "NES", "id": 49,  "location": null, "rotation": 0 } */
            let game = new Game();
            game.createFromApi(JSON.parse(GET_STATE_RESULT_FOR_N_3));

            let mazeCard = game.leftoverMazeCard;
            expect(mazeCard.outPaths).toEqual("NES");
            expect(mazeCard.id).toBe(49);
            expect(mazeCard.rotation).toBe(0);
        });

        it("maps player's objective to a flag on the correct maze card", () => {
            let game = new Game();
            game.createFromApi(JSON.parse(GET_STATE_RESULT_FOR_N_3));

            let objectiveMazeCard = game.mazeCardById(8);
            expect(objectiveMazeCard.hasObject).toBeTruthy();
        });

        it("only sets one maze card's objective flag to true", () => {
            let game = new Game();
            game.createFromApi(JSON.parse(GET_STATE_RESULT_FOR_N_3));

            let count = 0;
            for (let row = 0; row < game.n; row++) {
                for (let col = 0; col < game.n; col++) {
                    if (game.getMazeCard(loc(row, col)).hasObject) {
                        count++;
                    }
                }
            }
            expect(count).toBe(1);
        });

        it("sets objective flag for maze card id 0", () => {
            let apiState = JSON.parse(GET_STATE_RESULT_FOR_N_3);
            apiState.objectiveMazeCardId = 0;
            let game = new Game();
            game.createFromApi(apiState);

            let objectiveMazeCard = game.mazeCardById(0);
            expect(objectiveMazeCard.hasObject).toBeTruthy();
        });

        it("assigns to each player the pieceIndex as colorIndex", () => {
            let game = new Game();
            game.createFromApi(JSON.parse(GET_STATE_RESULT_FOR_N_3));
            expect(game.getPlayer(42).colorIndex).toEqual(0);
            expect(game.getPlayer(17).colorIndex).toEqual(1);
        });

        it("sets attributes for computer players", () => {
            let game = new Game();
            game.createFromApi(JSON.parse(GET_STATE_RESULT_FOR_N_3));
            let computerPlayer = game.getPlayer(42);
            expect(computerPlayer.isComputer).toBe(true);
            expect(computerPlayer.type).toBe("random");
            let player = game.getPlayer(17);
            expect(player.isComputer).toBe(false);
        });

        it("disables shift location, if enabled locations is missing one", () => {
            let game = new Game();
            game.createFromApi(JSON.parse(GET_STATE_RESULT_FOR_N_3));
            expect(game.disabledShiftLocation).toEqual({ column: 1, row: 2 });
        });

        it("sets disabled shift location to null if all locations are enabled", () => {
            let game = new Game();
            let apiState = JSON.parse(GET_STATE_RESULT_FOR_N_3);
            apiState.enabledShiftLocations.push({ column: 1, row: 2 });
            game.createFromApi(apiState);
            expect(game.disabledShiftLocation).toEqual(null);
        });
    });
});

function _assertPlayerLocation(game, id, location, mazeCardId) {
    let player = game.getPlayer(id);
    expect(game.getMazeCard(location)).toBe(player.mazeCard);
    expect(player.mazeCard.id).toBe(mazeCardId);
    expect(player.mazeCard.location).toEqual(location);
    expect(player.mazeCard.players.length).toEqual(1);
    expect(player.mazeCard.players).toEqual(expect.arrayContaining([player]));
}

function _buildMazeCardMatrix(game) {
    let mazeCards = [];
    let id = 0;
    for (let row = 0; row < game.n; row++) {
        game.mazeCards.push([]);
        for (let col = 0; col < game.n; col++) {
            let mazeCard = MazeCard.createNewRandom(id, row, col);
            mazeCards.push(mazeCard);
            game.mazeCards[row].push(mazeCard);
            id++;
        }
    }
    return mazeCards;
}

function _copyMazeCardMatrix(game) {
    let matrix = [];
    for (let row = 0; row < game.mazeCards.length; row++) {
        matrix.push([]);
        for (let col = 0; col < game.mazeCards[row].length; col++) {
            let mazeCard = game.getMazeCard(loc(row, col));
            matrix[row].push(mazeCard);
        }
    }
    return matrix;
}

function _addPlayer(game, location, id) {
    let originMazeCard = game.getMazeCard(location);
    let player = new Player(id, id);
    player.mazeCard = originMazeCard;
    originMazeCard.players.push(player);
    game.addPlayer(player);
    return player;
}

function _maxId(objs) {
    return objs.reduce((prev, cur) => Math.max(prev, cur.id), -1);
}

let GET_STATE_RESULT_FOR_N_3 = `{
  "maze": {
    "mazeSize": 3,
    "mazeCards": [{
        "outPaths": "NES",
        "id": 49,
        "location": null,
        "rotation": 0
    }, {
        "outPaths": "NES",
        "id": 0,
        "location": {
        "column": 0,
        "row": 0
        },
        "rotation": 180
    }, {
        "outPaths": "NE",
        "id": 1,
        "location": {
        "column": 1,
        "row": 0
        },
        "rotation": 180
    }, {
        "outPaths": "NS",
        "id": 2,
        "location": {
        "column": 2,
        "row": 0
        },
        "rotation": 90
    }, {
        "outPaths": "NE",
        "id": 7,
        "location": {
        "column": 0,
        "row": 1
        },
        "rotation": 180
    }, {
        "outPaths": "NE",
        "id": 8,
        "location": {
        "column": 1,
        "row": 1
        },
        "rotation": 270
    }, {
        "outPaths": "NS",
        "id": 9,
        "location": {
        "column": 2,
        "row": 1
        },
        "rotation": 0
    }, {
        "outPaths": "NS",
        "id": 14,
        "location": {
        "column": 0,
        "row": 2
        },
        "rotation": 180
    }, {
        "outPaths": "NES",
        "id": 15,
        "location": {
        "column": 1,
        "row": 2
        },
        "rotation": 180
    }, {
        "outPaths": "NE",
        "id": 16,
        "location": {
        "column": 2,
        "row": 2
        },
        "rotation": 0
    }]
  },
  "players": [{
    "id": 42,
    "mazeCardId": 16,
    "pieceIndex": 0,
    "isComputerPlayer": true,
    "algorithm": "random"
  },{
    "id": 17,
    "pieceIndex": 1,
    "mazeCardId": 15
  }],
  "objectiveMazeCardId": 8,
  "enabledShiftLocations": [
    {"column": 1, "row": 0},
    {"column": 0, "row": 1},
    {"column": 2, "row": 1}
  ],
  "nextAction": {
    "action": "SHIFT",
    "playerId": 17
  }
}`;
