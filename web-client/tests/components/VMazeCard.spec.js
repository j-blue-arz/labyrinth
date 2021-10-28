import { mount } from "@vue/test-utils";
import VMazeCard from "@/components/VMazeCard.vue";
import Player from "@/model/player.js";

beforeEach(() => {
    mockStore = createMockStore();
    mazeCard = { ...initialMazeCard };
    vMazeCard = undefined;
    givenNoObjective();
});

describe("VMazeCard", () => {
    it("contains an svg-element", () => {
        givenVMazeCard();

        expect(vMazeCard.contains("svg")).toBe(true);
    });

    it("has width of 100 if cardSize is 100", () => {
        givenVMazeCard();

        expect(vMazeCard.element.getAttribute("width")).toBe("100");
    });

    it("includes north outPath if MazeCard has a north outPath", () => {
        givenCardWithOutPaths("NW");
        givenVMazeCard();

        expect(vMazeCard.find({ ref: "north" }).exists()).toBeTruthy();
    });

    it("does not include north outPath if MazeCard object does not have a north outPath", () => {
        givenCardWithOutPaths("EW");
        givenVMazeCard();

        expect(vMazeCard.find({ ref: "north" }).exists()).toBeFalsy();
    });

    it("does not render players if the MazeCard object does not contain pieces", () => {
        givenVMazeCard();

        expect(vMazeCard.findAll("player-piece").length).toBe(0);
    });

    it("renders a single player", () => {
        givenPlayers([{ id: 0 }]);
        givenVMazeCard();

        expect(vMazeCard.findAll(".player-piece").length).toBe(1);
    });

    it("renders an objective if MazeCard has one", () => {
        givenObjective();
        givenVMazeCard();

        expect(vMazeCard.findAll(".objective").length).toBe(1);
    });

    it("does not render an objective if MazeCard has none", () => {
        givenNoObjective();
        givenVMazeCard();

        expect(vMazeCard.findAll(".objective").length).toBe(0);
    });
});

const mazeCardId = 1;
const initialMazeCard = { id: mazeCardId, outPaths: "NESW" };
let mazeCard = { ...initialMazeCard };
let vMazeCard;
let mockStore = createMockStore();

function createMockStore() {
    return {
        state: {
            game: {
                objectiveId: -1
            }
        },
        getters: {
            "players/findByMazeCard": id => []
        }
    };
}

function givenCardWithOutPaths(outPaths) {
    mazeCard = { ...mazeCard, outPaths: outPaths };
}

function givenVMazeCard() {
    vMazeCard = mount(VMazeCard, {
        propsData: { mazeCard: mazeCard },
        mocks: {
            $store: mockStore
        }
    });
}

function givenNoObjective() {
    mockStore.state.game.objectiveId = -1;
}

function givenObjective() {
    mockStore.state.game.objectiveId = mazeCardId;
}

function givenPlayers(players) {
    mockStore.getters["players/findByMazeCard"] = id => {
        if (id === mazeCardId) {
            return players;
        } else {
            return [];
        }
    };
}
