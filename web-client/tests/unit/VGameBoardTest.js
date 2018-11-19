import { mount } from "@vue/test-utils";
import VGameBoard from "@/components/VGameBoard.vue";
import VMazeCard from "@/components/VMazeCard.vue";
import MazeCard from "@/model/mazecard.js";

const mazeCardListFactory = function(n) {
    var mazeCards = [];
    var i = 0;
    for (var row = 0; row < n; row++) {
        for (var col = 0; col < n; col++) {
            mazeCards.push(new MazeCard(i++, row, col, "NS", 0));
        }
    }
    return mazeCards;
};

const findLowestPositionOfMazeCard = function(vGameBoard, dimension) {
    var toplevelPosition = parseInt(vGameBoard.element.getAttribute(dimension));
    var vMazeCards = vGameBoard.findAll(VMazeCard);
    var min = Number.MAX_VALUE;
    for (var i = 0; i < vMazeCards.length; i++) {
        var value = parseInt(vMazeCards.at(i).element.getAttribute(dimension));
        if (value < min) min = value;
    }
    return toplevelPosition + min;
};

describe("VGameBoard", () => {
    it("renders all VMazeCard components", () => {
        var gameBoard = mount(VGameBoard, {
            propsData: {
                n: 5,
                mazeCards: mazeCardListFactory(5),
                boardOffset: 100
            }
        });

        expect(gameBoard.findAll(VMazeCard).length).toBe(5 * 5);
    });

    it("renders leftmost v-maze-card exactly at given boardOffset prop", () => {
        var gameBoard = mount(VGameBoard, {
            propsData: {
                n: 7,
                mazeCards: mazeCardListFactory(7),
                boardOffset: 166
            }
        });

        var xPos = findLowestPositionOfMazeCard(gameBoard, "x");
        expect(xPos).toBe(166);
    });

    it("renders topmost v-maze-card exactly at given boardOffset prop", () => {
        var gameBoard = mount(VGameBoard, {
            propsData: {
                n: 5,
                mazeCards: mazeCardListFactory(5),
                boardOffset: 99
            }
        });
        var yPos = findLowestPositionOfMazeCard(gameBoard, "y");
        expect(yPos).toBe(99);
    });
});
