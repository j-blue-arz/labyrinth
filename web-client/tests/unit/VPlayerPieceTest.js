import { shallowMount } from "@vue/test-utils";
import VPlayerPiece from "@/components/VPlayerPiece.vue";
import Player from "@/model/player.js";

const wrapperFactory = function(player) {
    return shallowMount(VPlayerPiece, {
        propsData: {
            player: player,
            xCenterPos: 50,
            yCenterPos: 50,
            maxSize: 30
        }
    });
};

describe("VPlayerPiece", () => {
    it("renders different classes for different values of colorIndex", () => {
        for (let index = 0; index < 4; index++) {
            let player = new Player(index, index);
            let playerPiece = wrapperFactory(player);
            let svgElement = playerPiece.find({ ref: "playerPiece" });
            let expectedClass = "player-piece__player-" + index;
            expect(svgElement.classes()).toContain(expectedClass);
        }
    });

    it("assigns a class to the piece of the user", () => {
        let player = new Player(0, 2);
        player.isUser = true;
        let playerPiece = wrapperFactory(player);
        let svgElement = playerPiece.find({ ref: "playerPiece" });
        let expectedClass = "player-piece__user";
        expect(svgElement.classes()).toContain(expectedClass);
    });

    it("does not assign user class to pieces who are not owned by the user", () => {
        let player = new Player(0, 2);
        player.isUser = false;
        let playerPiece = wrapperFactory(player);
        let svgElement = playerPiece.find({ ref: "playerPiece" });
        svgElement.classes().forEach(elementClass => {
            expect(elementClass).toEqual(
                expect.not.stringContaining("player-piece__user")
            );
        });
    });

    it("assigns a class to the piece of the user, when it is his time to move", () => {
        let player = new Player(0, 2);
        player.isUser = true;
        player.turnAction = "MOVE";
        let playerPiece = wrapperFactory(player);
        let svgElement = playerPiece.find({ ref: "playerPiece" });
        let expectedClass = "player-piece__user--to-move";
        expect(svgElement.classes()).toContain(expectedClass);
    });
});
