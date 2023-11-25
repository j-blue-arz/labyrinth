import VPlayerPiece from "@/components/VPlayerPiece.vue";
import { shallowMount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

const wrapperFactory = function (player) {
    return shallowMount(VPlayerPiece, {
        props: {
            player: player,
            interaction: false,
        },
    });
};

describe("VPlayerPiece", () => {
    it("renders different classes for different values of pieceIndex", () => {
        for (let index = 0; index < 4; index++) {
            let player = { id: index, pieceIndex: index };
            let playerPiece = wrapperFactory(player);
            let svgElement = playerPiece.find({ ref: "playerPiece" });
            let expectedClass = "player-piece__player-" + index;
            expect(svgElement.classes()).toContain(expectedClass);
        }
    });

    it("assigns a class to the piece of the user", () => {
        let player = { id: 0, isUser: true };
        let playerPiece = wrapperFactory(player);
        let svgElement = playerPiece.find({ ref: "playerPiece" });
        let textElement = svgElement.find("text");
        expect(textElement.classes()).toContain("player-piece--is-user");
    });

    it("does not assign user class to pieces who are not owned by the user", () => {
        let player = { id: 0, isUser: false };
        let playerPiece = wrapperFactory(player);
        let svgElement = playerPiece.find({ ref: "playerPiece" });
        svgElement.classes().forEach((elementClass) => {
            expect(elementClass).toEqual(expect.not.stringContaining("player-piece--is-user"));
        });
    });
});
