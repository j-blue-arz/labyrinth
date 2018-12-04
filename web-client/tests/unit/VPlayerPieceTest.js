import { shallowMount } from "@vue/test-utils";
import VPlayerPiece from "@/components/VPlayerPiece.vue";

const wrapperFactory = function(index) {
    return shallowMount(VPlayerPiece, {
        propsData: {
            playerIndex: index,
            xCenterPos: 50,
            yCenterPos: 50,
            maxSize: 30
        }
    });
};

describe("VPlayerPiece", () => {
    it("renders different classes for different values of playerIndex", () => {
        for (let index = 0; index < 4; index++) {
            let playerPiece = wrapperFactory(index);
            let svgElement = playerPiece.find({ ref: "playerPiece" });
            let expectedClass = "player-piece__player-" + index;
            expect(svgElement.classes()).toContain(expectedClass);
        }
    });
});
