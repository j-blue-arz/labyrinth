import VMazeCard from "@/components/VMazeCard.vue";
import { useGameStore } from "@/stores/game.js";
import { usePlayersStore } from "@/stores/players.js";
import { createTestingPinia } from "@pinia/testing";
import { mount } from "@vue/test-utils";
import { beforeEach, describe, expect, it, vi } from "vitest";

beforeEach(() => {
    testingPinia = createTestingPinia({
        game: {
            objectiveId: -1,
        },
        createSpy: vi.fn,
    });
    gameStore = useGameStore();
    playersStore = usePlayersStore();
    playersStore.findByMazeCard = () => [];
    mazeCard = { ...initialMazeCard };
    givenNoObjective();
});

describe("VMazeCard", () => {
    it("contains an svg-element", () => {
        whenCreateVMazeCard();

        expect(vMazeCard.find("svg").exists()).toBe(true);
    });

    it("has width of 100 if cardSize is 100", () => {
        whenCreateVMazeCard();

        expect(vMazeCard.element.getAttribute("width")).toBe("100");
    });

    it("includes north outPath if MazeCard has a north outPath", () => {
        givenCardWithOutPaths("NW");

        whenCreateVMazeCard();

        expect(vMazeCard.find({ ref: "north" }).exists()).toBeTruthy();
    });

    it("does not include north outPath if MazeCard object does not have a north outPath", () => {
        givenCardWithOutPaths("EW");

        whenCreateVMazeCard();

        expect(vMazeCard.find({ ref: "north" }).exists()).toBeFalsy();
    });

    it("does not render players if the MazeCard object does not contain pieces", () => {
        whenCreateVMazeCard();

        expect(vMazeCard.findAll("player-piece").length).toBe(0);
    });

    it("renders a single player", () => {
        givenPlayers([{ id: 0 }]);

        whenCreateVMazeCard();

        expect(vMazeCard.findAll(".player-piece").length).toBe(1);
    });

    it("renders an objective if MazeCard has one", () => {
        givenObjective();

        whenCreateVMazeCard();

        expect(vMazeCard.findAll(".objective").length).toBe(1);
    });

    it("does not render an objective if MazeCard has none", () => {
        givenNoObjective();

        whenCreateVMazeCard();

        expect(vMazeCard.findAll(".objective").length).toBe(0);
    });
});

const mazeCardId = 1;
const initialMazeCard = { id: mazeCardId, outPaths: "NESW" };
let mazeCard = { ...initialMazeCard };
let vMazeCard;

let testingPinia;
let gameStore;
let playersStore;

function givenCardWithOutPaths(outPaths) {
    mazeCard = { ...mazeCard, outPaths: outPaths };
}

const whenCreateVMazeCard = function () {
    vMazeCard = mount(VMazeCard, {
        props: { mazeCard: mazeCard },
        global: {
            plugins: [testingPinia],
        },
    });
};

function givenNoObjective() {
    gameStore.objectiveId = -1;
}

function givenObjective() {
    gameStore.objectiveId = mazeCardId;
}

function givenPlayers(players) {
    playersStore.findByMazeCard = (id) => {
        if (id === mazeCardId) {
            return players;
        } else {
            return [];
        }
    };
}
