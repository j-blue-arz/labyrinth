import { state, mutations } from "@/store/modules/game.js";

describe("mutations", () => {
    describe("update", () => {
        it("results in a game with two players", () => {
            givenInitialGameState();
            givenApiStateWithSize3();

            whenCreateFromApi();

            expect(game.playerIds).toContain(42);
            expect(game.playerIds).toContain(17);
        });

        it("sets objective flag for maze card id 8", () => {
            givenInitialGameState();
            givenApiStateWithSize3();

            whenCreateFromApi();

            expect(game.objectiveId).toBe(8);
        });

        it("sets next action from api", () => {
            givenInitialGameState();
            givenApiStateWithSize3();

            whenCreateFromApi();

            expect(game.nextAction).toBe(apiState.nextAction);
        });

        it("marks game as served by backend", () => {
            givenInitialGameState();
            givenApiStateWithSize3();

            whenCreateFromApi();

            expect(game.isServed).toBe(true);
        });
    });
});

const { update } = mutations;

let game;
let apiState;

const givenInitialGameState = function() {
    game = state();
};

const givenApiStateWithSize3 = function() {
    apiState = JSON.parse(GET_STATE_RESULT_FOR_N_3);
};

const whenCreateFromApi = function() {
    update(game, apiState);
};

const GET_STATE_RESULT_FOR_N_3 = `{
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
      "isBot": true,
      "computationMethod": "random"
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
