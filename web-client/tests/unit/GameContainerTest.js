import { mount } from "@vue/test-utils";
import GameContainer from "@/components/GameContainer.vue";
import VMazeCard from "@/components/VMazeCard.vue";
import VPlayerPiece from "@/components/VPlayerPiece.vue";

const extractIdMatrix = function(gameContainer) {
    var vMazeCards = gameContainer
        .find({ ref: "interactive-board" })
        .findAll(VMazeCard);
    var htmlCards = [];
    for (var i = 0; i < vMazeCards.length; i++) {
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
    var vMazeCards = gameContainer
        .find({ ref: "interactive-board" })
        .findAll(VMazeCard);
    var vPlayerPieces = gameContainer.findAll(VPlayerPiece);
    for (var i = 0; i < vPlayerPieces.length; i++) {
        mazeCardIds.push(
            Number.parseInt(
                vPlayerPieces.at(0).element.parentElement.getAttribute("id")
            )
        );
    }
    return mazeCardIds;
};

describe("GameContainer", () => {
    it("rotates leftover maze card when clicked", () => {
        var gameContainer = mount(GameContainer);
        const rotateOperation = jest.spyOn(
            gameContainer.vm.$data.leftoverMazeCard,
            "rotateClockwise"
        );
        var leftOverVMazeCard = gameContainer.find({ ref: "leftover" });
        leftOverVMazeCard.trigger("click");
        expect(rotateOperation).toHaveBeenCalledTimes(1);
    });

    it("shifts leftmost row correctly to the south", () => {
        var gameContainer = mount(GameContainer);
        var idMatrixOld = extractIdMatrix(gameContainer);
        var interactiveBoard = gameContainer.find({ ref: "interactive-board" });

        interactiveBoard.vm.$emit("insert-card", { row: -1, column: 1 });
        var idMatrixNew = extractIdMatrix(gameContainer);

        expect(idMatrixNew[1][1]).toBe(idMatrixOld[0][1]);
        expect(idMatrixNew[2][1]).toBe(idMatrixOld[1][1]);
        expect(idMatrixNew[3][1]).toBe(idMatrixOld[2][1]);
        expect(idMatrixNew[4][1]).toBe(idMatrixOld[3][1]);
        expect(idMatrixNew[5][1]).toBe(idMatrixOld[4][1]);
        expect(idMatrixNew[6][1]).toBe(idMatrixOld[5][1]);
    });

    it("inserts leftover card when shifting", () => {
        var gameContainer = mount(GameContainer);
        var oldLeftOverId = determineLeftOverId(gameContainer);
        var interactiveBoard = gameContainer.find({ ref: "interactive-board" });

        interactiveBoard.vm.$emit("insert-card", { row: -1, column: 3 });
        var idMatrixNew = extractIdMatrix(gameContainer);

        expect(idMatrixNew[0][3]).toBe(oldLeftOverId);
    });

    it("updates leftover correctly card when shifting", () => {
        var gameContainer = mount(GameContainer);
        var idMatrixOld = extractIdMatrix(gameContainer);
        var interactiveBoard = gameContainer.find({ ref: "interactive-board" });

        interactiveBoard.vm.$emit("insert-card", { row: 5, column: -1 });
        var newLeftOverId = determineLeftOverId(gameContainer);

        expect(newLeftOverId).toBe(idMatrixOld[5][6]);
    });

    it("displays a player piece on the correct maze card", () => {
        var gameContainer = mount(GameContainer, {
            propsData: {
                initialPlayerLocations: [{ row: 6, column: 1 }]
            }
        });
        var mazeCardIds = determineMazeCardIdsWithPlayers(gameContainer);
        expect(mazeCardIds.length).toBe(1);
        var idMatrix = extractIdMatrix(gameContainer);
        expect(mazeCardIds[0]).toBe(idMatrix[6][1]);
    });

    it("moves players to opposing side of the board when shifted out", () => {
        var gameContainer = mount(GameContainer, {
            propsData: {
                initialPlayerLocations: [{ row: 6, column: 1 }]
            }
        });

        var leftoverCardId = determineLeftOverId(gameContainer);
        var interactiveBoard = gameContainer.find({ ref: "interactive-board" });

        interactiveBoard.vm.$emit("insert-card", { row: -1, column: 1 });

        var mazeCardIds = determineMazeCardIdsWithPlayers(gameContainer);
        expect(mazeCardIds.length).toBe(1);
        expect(mazeCardIds[0]).toBe(leftoverCardId);
    });


    it("moves players when maze card is clicked", () => {
        var gameContainer = mount(GameContainer, {
            propsData: {
                initialPlayerLocations: [{ row: 6, column: 1 }]
            }
        });

        var interactiveBoard = gameContainer.find({ ref: "interactive-board" });
        interactiveBoard.vm.$emit("move-piece", { row: 4, column: 4 })

        var mazeCardIds = determineMazeCardIdsWithPlayers(gameContainer);
        expect(mazeCardIds.length).toBe(1);
        var idMatrix = extractIdMatrix(gameContainer);
        expect(mazeCardIds[0]).toBe(idMatrix[4][4]);
    });
});
