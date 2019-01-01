import { mount } from "@vue/test-utils";
import GameContainer from "@/components/GameContainer.vue";
import VPlayerPiece from "@/components/VPlayerPiece.vue";
import InteractiveBoard from "@/components/InteractiveBoard.vue";
import GameFactory from "@/model/gameFactory";
import { loc, extractIdMatrix } from "./testutils.js";

const determineLeftOverId = function(gameContainer) {
    let board = gameContainer.find(InteractiveBoard);
    return Number.parseInt(board.find({ ref: "leftover" }).element.getAttribute("id"));
};

const determineMazeCardIdsWithPlayers = function(gameContainer) {
    var mazeCardIds = [];
    var vPlayerPieces = gameContainer.findAll(VPlayerPiece);
    for (var i = 0; i < vPlayerPieces.length; i++) {
        mazeCardIds.push(
            Number.parseInt(
                vPlayerPieces.at(i).element.parentElement.parentElement.getAttribute("id")
            )
        );
    }
    return mazeCardIds;
};

const factory = function(locations) {
    if (locations === undefined) {
        locations = [];
    }
    return mount(GameContainer, {
        propsData: {
            gameFactory: new GameFactory(locations),
            shouldUseApi: false
        }
    });
};

const shiftEvent = function(row, column, rotation) {
    return { location: loc(row, column), leftoverRotation: rotation };
};

describe("GameContainer", () => {
    it("shifts leftmost row correctly to the south", () => {
        var gameContainer = factory();
        var idMatrixOld = extractIdMatrix(gameContainer);
        var interactiveBoard = gameContainer.find({ ref: "interactive-board" });

        interactiveBoard.vm.$emit("insert-card", shiftEvent(0, 1, 0));
        var idMatrixNew = extractIdMatrix(gameContainer);

        expect(idMatrixNew[1][1]).toBe(idMatrixOld[0][1]);
        expect(idMatrixNew[2][1]).toBe(idMatrixOld[1][1]);
        expect(idMatrixNew[3][1]).toBe(idMatrixOld[2][1]);
        expect(idMatrixNew[4][1]).toBe(idMatrixOld[3][1]);
        expect(idMatrixNew[5][1]).toBe(idMatrixOld[4][1]);
        expect(idMatrixNew[6][1]).toBe(idMatrixOld[5][1]);
    });

    it("inserts leftover card when shifting", () => {
        var gameContainer = factory();
        var oldLeftOverId = determineLeftOverId(gameContainer);
        var interactiveBoard = gameContainer.find({ ref: "interactive-board" });

        interactiveBoard.vm.$emit("insert-card", shiftEvent(0, 3, 0));
        var idMatrixNew = extractIdMatrix(gameContainer);

        expect(idMatrixNew[0][3]).toBe(oldLeftOverId);
    });

    it("updates leftover correctly card when shifting", () => {
        var gameContainer = factory();
        var idMatrixOld = extractIdMatrix(gameContainer);
        var interactiveBoard = gameContainer.find({ ref: "interactive-board" });

        interactiveBoard.vm.$emit("insert-card", shiftEvent(5, 0, 0));
        var newLeftOverId = determineLeftOverId(gameContainer);

        expect(newLeftOverId).toBe(idMatrixOld[5][6]);
    });

    it("displays a player piece on the correct maze card", () => {
        var gameContainer = factory([loc(5, 1)]);
        var playerCardIds = determineMazeCardIdsWithPlayers(gameContainer);
        expect(playerCardIds.length).toBe(1);
        var idMatrix = extractIdMatrix(gameContainer);
        expect(playerCardIds[0]).toBe(idMatrix[5][1]);
    });

    it("moves players with maze cards when shifted", () => {
        var gameContainer = factory([loc(4, 3)]);

        var interactiveBoard = gameContainer.find({ ref: "interactive-board" });
        interactiveBoard.vm.$emit("insert-card", shiftEvent(0, 3, 0));

        var playerCardIds = determineMazeCardIdsWithPlayers(gameContainer);
        expect(playerCardIds.length).toBe(1);
        var idMatrix = extractIdMatrix(gameContainer);
        expect(playerCardIds[0]).toBe(idMatrix[5][3]);
    });

    it("moves players to opposing side of the board when shifted out", () => {
        var gameContainer = factory([loc(6, 1)]);

        var pushedInCardId = determineLeftOverId(gameContainer);
        var interactiveBoard = gameContainer.find({ ref: "interactive-board" });

        interactiveBoard.vm.$emit("insert-card", shiftEvent(0, 1, 0));

        var playerCardIds = determineMazeCardIdsWithPlayers(gameContainer);
        expect(playerCardIds.length).toBe(1);
        expect(playerCardIds[0]).toBe(pushedInCardId);
    });

    it("moves players when maze card is clicked", () => {
        var gameContainer = factory([loc(0, 1)]);

        var interactiveBoard = gameContainer.find({ ref: "interactive-board" });
        interactiveBoard.vm.$emit("move-piece", loc(4, 4));

        var playerCardIds = determineMazeCardIdsWithPlayers(gameContainer);
        expect(playerCardIds.length).toBe(1);
        var idMatrix = extractIdMatrix(gameContainer);
        expect(playerCardIds[0]).toBe(idMatrix[4][4]);
    });

    it("assigns colors to all VPlayerPiece components ascending from 0", () => {
        let playerLocations = [loc(0, 0), loc(0, 1), loc(0, 2), loc(0, 3)];
        let gameContainer = factory(playerLocations);
        let vPlayerPieces = gameContainer.findAll(VPlayerPiece);
        let playerColors = new Set();
        for (let i = 0; i < vPlayerPieces.length; i++) {
            playerColors.add(vPlayerPieces.at(i).props("player").colorIndex);
        }
        expect(playerColors.size).toBe(4);
        for (let i = 0; i < vPlayerPieces.length; i++) {
            expect(playerColors).toContain(i);
        }
    });

    it("does not show game menu button", () => {
        let gameContainer = factory();
        expect(gameContainer.find(".game-menu__button").exists()).toBe(false);
    });
});
