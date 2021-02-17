import { shallowMount, mount } from "@vue/test-utils";
import LeftoverMazeCard from "@/components/LeftoverMazeCard.vue";
import VMazeCard from "@/components/VMazeCard.vue";
import MazeCard from "@/model/mazeCard.js";
import { copyObjectStructure } from "./testutils.js";

beforeEach(() => {
    leftoverMazeCard = factory();
});

describe("InteractiveBoard", () => {
    it("rotates leftover maze card when clicked", () => {
        givenRotation(0);
        givenInteraction(true);

        whenMazeCardIsClicked();

        thenRotationIs(90);
    });

    it("does not rotate leftover maze card given no interaction required", () => {
        givenRotation(0);
        givenInteraction(false);

        whenMazeCardIsClicked();

        thenRotationIs(0);
    });

    it("assigns class 'interaction' on leftover maze card when interaction is required", () => {
        givenInteraction(true);

        thenMazeCardIsInteractive();
    });

    it("removes class 'interaction' on leftover maze card when no interaction required", () => {
        givenInteraction(false);

        thenMazeCardIsNotInteractive();
    });
});

let leftoverMazeCard = null;

const mazeCard = new MazeCard(0, -1, -1, "NS", 0);

const factory = function(interaction) {
    let leftoverMazeCard = mount(LeftoverMazeCard, {
        propsData: {
            mazeCard: mazeCard,
            interaction: interaction
        }
    });
    return leftoverMazeCard;
};

const givenRotation = function(rotation) {
    mazeCard.rotation = rotation;
};

const givenInteraction = function(isInteraction) {
    leftoverMazeCard = factory(isInteraction);
};

const whenMazeCardIsClicked = function() {
    leftoverMazeCard.find(VMazeCard).trigger("click");
};

const thenRotationIs = function(rotation) {
    expect(mazeCard.rotation).toEqual(rotation);
};

const thenMazeCardIsInteractive = function() {
    let leftoverVMazeCard = leftoverMazeCard.find(VMazeCard);
    expect(leftoverVMazeCard.classes()).toContain("maze-card--interactive");
};

const thenMazeCardIsNotInteractive = function() {
    let leftoverVMazeCard = leftoverMazeCard.find(VMazeCard);
    expect(leftoverVMazeCard.classes()).not.toContain("maze-card--interactive");
};
