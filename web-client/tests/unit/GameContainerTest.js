import { mount } from "@vue/test-utils";
import GameContainer from "@/components/GameContainer.vue";
import VMazeCard from "@/components/VMazeCard.vue";
import VPlayerPiece from "@/components/VPlayerPiece.vue";
import GameFactory from "@/model/gameFactory";
import MOVE_ACTION from "@/model/player";
import { loc } from "./testutils.js";

const extractIdMatrix = function(gameContainer) {
    var vMazeCards = gameContainer
        .find({ ref: "interactive-board" })
        .findAll(VMazeCard);
    var htmlCards = [];
    for (let i = 0; i < vMazeCards.length; i++) {
        var card = vMazeCards.at(i);
        var x = Number.parseInt(card.element.getAttribute("x"));
        var y = Number.parseInt(card.element.getAttribute("y"));
        var id = Number.parseInt(card.element.getAttribute("id"));
        htmlCards.push({
            x: x,
            y: y,
            id: id
        });
    }
    htmlCards.sort(function(a, b) {
        if (a.y > b.y) {
            return 1;
        }
        if (a.y < b.y) {
            return -1;
        }
        if (a.x > b.x) {
            return 1;
        }
        if (a.x < b.x) {
            return -1;
        }
        return 0;
    });
    var ids = [];
    var i = 0;
    for (var row = 0; row < 7; row++) {
        ids.push([]);
        for (var col = 0; col < 7; col++) {
            ids[row].push(htmlCards[i++].id);
        }
    }
    return ids;
};

const determineLeftOverId = function(gameContainer) {
    return Number.parseInt(
        gameContainer.find({ ref: "leftover" }).element.getAttribute("id")
    );
};

const determineMazeCardIdsWithPlayers = function(gameContainer) {
    var mazeCardIds = [];
    var vPlayerPieces = gameContainer.findAll(VPlayerPiece);
    for (var i = 0; i < vPlayerPieces.length; i++) {
        mazeCardIds.push(
            Number.parseInt(
                vPlayerPieces.at(i).element.parentElement.getAttribute("id")
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
            gameFactory: new GameFactory(locations)
        }
    });
};

describe("GameContainer", () => {
    it("rotates leftover maze card when clicked", () => {
        var gameContainer = factory();
        const rotateOperation = jest.spyOn(
            gameContainer.vm.$data.game.leftoverMazeCard,
            "rotateClockwise"
        );
        var leftOverVMazeCard = gameContainer.find({ ref: "leftover" });
        var oldRotation = leftOverVMazeCard.props().mazeCard.rotation;
        leftOverVMazeCard.trigger("click");
        var newRotation = leftOverVMazeCard.props().mazeCard.rotation;
        expect(newRotation).toBe((oldRotation + 90) % 360);
        expect(rotateOperation).toHaveBeenCalledTimes(1);
    });

    it("does not rotate leftover maze card when next action is move", () => {
        var gameContainer = factory();
        const rotateOperation = jest.spyOn(
            gameContainer.vm.$data.game.leftoverMazeCard,
            "rotateClockwise"
        );
        gameContainer.vm.$data.game.getPlayer(0).nextAction = MOVE_ACTION;
        var leftOverVMazeCard = gameContainer.find({ ref: "leftover" });
        leftOverVMazeCard.trigger("click");
        expect(rotateOperation).toHaveBeenCalledTimes(0);
    });

    it("shifts leftmost row correctly to the south", () => {
        var gameContainer = factory();
        var idMatrixOld = extractIdMatrix(gameContainer);
        var interactiveBoard = gameContainer.find({ ref: "interactive-board" });

        interactiveBoard.vm.$emit("insert-card", loc(0, 1));
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

        interactiveBoard.vm.$emit("insert-card", loc(0, 3));
        var idMatrixNew = extractIdMatrix(gameContainer);

        expect(idMatrixNew[0][3]).toBe(oldLeftOverId);
    });

    it("updates leftover correctly card when shifting", () => {
        var gameContainer = factory();
        var idMatrixOld = extractIdMatrix(gameContainer);
        var interactiveBoard = gameContainer.find({ ref: "interactive-board" });

        interactiveBoard.vm.$emit("insert-card", loc(5, 0));
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
        interactiveBoard.vm.$emit("insert-card", loc(0, 3));

        var playerCardIds = determineMazeCardIdsWithPlayers(gameContainer);
        expect(playerCardIds.length).toBe(1);
        var idMatrix = extractIdMatrix(gameContainer);
        expect(playerCardIds[0]).toBe(idMatrix[5][3]);
    });

    it("moves players to opposing side of the board when shifted out", () => {
        var gameContainer = factory([loc(6, 1)]);

        var pushedInCardId = determineLeftOverId(gameContainer);
        var interactiveBoard = gameContainer.find({ ref: "interactive-board" });

        interactiveBoard.vm.$emit("insert-card", loc(0, 1));

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

    it("assigns indicies to all VPlayerPiece components ascending from 0", () => {
        let playerLocations = [loc(0, 0), loc(0, 1), loc(0, 2), loc(0, 3)];
        let gameContainer = factory(playerLocations);
        let vPlayerPieces = gameContainer.findAll(VPlayerPiece);
        let playerIndices = new Set();
        for (let i = 0; i < vPlayerPieces.length; i++) {
            playerIndices.add(vPlayerPieces.at(i).props("playerIndex"));
        }
        expect(playerIndices.size).toBe(4);
        for (let i = 0; i < vPlayerPieces.length; i++) {
            expect(playerIndices).toContain(i);
        }
    });
});
