export const MOVE_ACTION = "MOVE";
export const SHIFT_ACTION = "SHIFT";
export const NO_ACTION = "NONE";

export function getLabel(player) {
    if (player.isBot) {
        return computationMethodLabel(player.computationMethod);
    } else if (player.name) {
        return player.name;
    } else if (player.isWasm) {
        return "WASM: Exhaustive Search";
    }
    return "";
}

export function computationMethodLabel(computationMethod) {
    if (computationMethod === "libexhsearch") {
        return "Exhaustive Search (1P)";
    } else if (computationMethod === "libminimax") {
        return "Minimax (2P)";
    } else if (computationMethod.startsWith("libminimax-")) {
        let suffix = computationMethod.replace("libminimax-", "");
        if (suffix === "distance") {
            return "Minimax (2P) - Distance Heuristic";
        } else if (suffix === "reachable") {
            return "Minimax (2P) - Reachable Heuristic";
        } else {
            return "Minimax (2P) - heuristic: " + suffix;
        }
    } else if (computationMethod === "wasm") {
        return "WASM: Exhaustive Search\u00A0(1P)";
    } else {
        return computationMethod;
    }
}
