import { shallowMount } from "@vue/test-utils";
import VPlayerPiece from "@/components/VPlayerPiece.vue";
import Player from "@/model/player.js";

const wrapperFactory = function(player) {
    return shallowMount(VPlayerPiece, {
        propsData: {
            player: player,
            maxSize: 30,
            interaction: player.hasToMove()
        }
    });
};

describe("VPlayerPiece", () => {
    it("renders different classes for different values of pieceIndex", () => {
        for (let index = 0; index < 4; index++) {
            let player = new Player(index);
            player.pieceIndex = index;
            let playerPiece = wrapperFactory(player);
            let svgElement = playerPiece.find({ ref: "playerPiece" });
            let expectedClass = "player-piece__player-" + index;
            expect(svgElement.classes()).toContain(expectedClass);
        }
    });

    it("assigns a class to the piece of the user", () => {
        let player = new Player(0);
        player.isUser = true;
        let playerPiece = wrapperFactory(player);
        let svgElement = playerPiece.find({ ref: "playerPiece" });
        let textElement = svgElement.find("text");
        expect(textElement.classes()).toContain("player-piece--is-user");
    });

    it("does not assign user class to pieces who are not owned by the user", () => {
        let player = new Player(0);
        player.isUser = false;
        let playerPiece = wrapperFactory(player);
        let svgElement = playerPiece.find({ ref: "playerPiece" });
        svgElement.classes().forEach(elementClass => {
            expect(elementClass).toEqual(expect.not.stringContaining("player-piece--is-user"));
        });
    });
});
