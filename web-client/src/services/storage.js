export const USER_PLAYER = "user";
export const WASM_PLAYER = "wasm";

const _key = function(type) {
    return `${type}PlayerId`;
};

const _delete = function(type) {
    if (useStorage) {
        sessionStorage.removeItem(_key(type));
    }
};

let useStorage = false;

export default {
    useStorage() {
        useStorage = true;
    },

    set(type, playerId) {
        if (useStorage) {
            sessionStorage.setItem(_key(type), playerId);
        }
    },

    deleteId(playerId) {
        for (const type of [USER_PLAYER, WASM_PLAYER]) {
            if (this.get(type) === playerId) {
                _delete(type);
            }
        }
    },

    get(type) {
        if (useStorage) {
            return parseInt(sessionStorage.getItem(_key(type)));
        } else {
            return null;
        }
    },

    has(type) {
        if (useStorage) {
            return Boolean(sessionStorage.getItem(_key(type)));
        } else {
            return false;
        }
    },

    hasAny() {
        return this.has(USER_PLAYER) || this.has(WASM_PLAYER);
    }
};
