let instance = null;

export default class WasmGateway {
    constructor() {
        if (!instance) {
            instance = this;
        }
        this.libexhsearch = null;
        this.isLoading = false;
        this.publicPath = process.env.BASE_URL;
        return instance;
    }

    hasLibexhsearch() {
        return this.libexhsearch !== null;
    }

    loadLibexhsearch(callback) {
        if (!this.libexhsearch && !this.isLoading) {
            this.isLoading = true;
            this._loadRuntime()
                .then((loadWasm) => {
                    loadWasm().then((libexhsearch) => {
                        this.libexhsearch = libexhsearch;
                        this.isLoading = false;
                        callback();
                    });
                })
                .catch((reason) => {
                    console.error("failed to load runtime: " + reason);
                    this.isLoading = false;
                })
                .then(() => {
                    this.isLoading = false;
                });
        }
    }

    computeActions(instance) {
        let vectorNodes = new this.libexhsearch.vectorOfNode();
        for (const mazeCard of instance.mazeCardList) {
            vectorNodes.push_back(this._createNode(mazeCard));
        }

        let mazeGraph = new this.libexhsearch.MazeGraph(vectorNodes);
        for (const location of instance.shiftLocations) {
            mazeGraph.addShiftLocation(location);
        }

        const action = this.libexhsearch.findBestAction(
            mazeGraph,
            instance.playerLocation,
            instance.objectiveId,
            instance.previousShiftLocation ?? this._loc(-1, -1)
        );

        const computedActions = {
            shiftAction: {
                location: this._loc(action.shift.location.row, action.shift.location.column),
                leftoverRotation: action.shift.rotation,
            },
            moveLocation: this._loc(action.move_location.row, action.move_location.column),
        };

        mazeGraph.delete();
        for (let i = 0; i < vectorNodes.size(); ++i) {
            vectorNodes.get(i).delete();
        }
        vectorNodes.delete();

        return computedActions;
    }

    _createNode(mazeCard) {
        let id = mazeCard.id;
        let outPathBitmask = 0;
        if (this._hasOutPath(mazeCard, "N")) {
            outPathBitmask += 1;
        }
        if (this._hasOutPath(mazeCard, "E")) {
            outPathBitmask += 2;
        }
        if (this._hasOutPath(mazeCard, "S")) {
            outPathBitmask += 4;
        }
        if (this._hasOutPath(mazeCard, "W")) {
            outPathBitmask += 8;
        }
        let rotation = mazeCard.rotation;
        return new this.libexhsearch.Node(id, outPathBitmask, rotation);
    }

    _loc(row, column) {
        return { row: row, column: column };
    }

    _loadRuntime() {
        return new Promise((resolve, reject) => {
            const url =
                location.protocol + "//" + location.host + this.publicPath + "wasm/libexhsearch.js";
            const script = document.createElement("script");
            script.type = "text/javascript";
            script.async = true;
            script.addEventListener("load", () => {
                resolve(window["libexhsearch"]);
            });
            script.addEventListener("error", () => {
                reject(new Error(`Error loading ${url}`));
            });
            script.src = url;
            document.body.appendChild(script);
            this.scriptElement = script;
        });
    }

    _hasOutPath(mazeCard, outPath) {
        return mazeCard.outPaths.indexOf(outPath) != -1;
    }
}
