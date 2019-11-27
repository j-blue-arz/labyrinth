import { WasmWrapper } from "@/assets/wrapper.js";

class Location {
    constructor(row, column) {
        this.row = row;
        this.column = column;
    }

    toString() {
        return "(" + this.row + ", " + this.column + ")";
    }
}

class MazeCard {
    constructor(id, doors, rotation) {
        this.id = id;
        this.doors = doors;
        this.rotation = rotation;
    }

    getOutPathsBitmask() {
        let result = 0;
        for (let door = 0; door < 4; door++) {
            if (this.doors.indexOf("NESW".charAt(door)) != -1) {
                result += 1 >> door;
            }
        }
        return result;
    }
}

class Graph {
    constructor(extent, mazeCards, leftoverMazeCard) {
        this.extent = extent;
        this.mazeCards = mazeCards;
        this.leftoverMazeCard = leftoverMazeCard;
    }

    linearizedMazeCards() {
        let result = [].concat.apply([], this.mazeCards);
        result.push(this.leftoverMazeCard);
        return result;
    }
}

class ExhsearchWrapper extends WasmWrapper {
    constructor(wasmInstance, memory) {
        super(wasmInstance, memory);
        this.bindings = {
            structLocation: {
                types: ["i16", "i16"],
                jsConstructor: (row, column) => new Location(row, column),
                memberGetters: [location => location.row, location => location.column]
            },
            structNode: {
                types: ["i32", "i32", "i32"],
                memberGetters: [
                    mazeCard => mazeCard.id,
                    mazeCard => mazeCard.getOutPathsBitmask(),
                    mazeCard => mazeCard.rotation
                ]
            },
            structGraph: {
                types: ["i32", "i32", "structNode*"],
                memberGetters: [
                    graph => graph.extent,
                    graph => graph.extent * graph.extent + 1,
                    graph => graph.linearizedMazeCards()
                ]
            },
            structAction: {
                types: ["structLocation", "i16", "structLocation"],
                jsConstructor: (shiftLocation, rotation, moveLocation) => {
                    return {
                        shiftLocation: shiftLocation,
                        rotation: rotation,
                        moveLocation: moveLocation
                    };
                }
            }
        };
    }

    findAction(graph, startLocation, objectiveId, previousShiftLocation) {
        return this._callC(
            "find_action",
            "structAction",
            ["structGraph", "structLocation", "i32", "structLocation"],
            [graph, startLocation, objectiveId, previousShiftLocation]
        );
    }
}

export { ExhsearchWrapper, Graph, MazeCard, Location };
