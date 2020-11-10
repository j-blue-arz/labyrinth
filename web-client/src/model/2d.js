/**
 * Contains classes and constants for elemental 2D computation.
 * The origin is at the top left corner.
 */
export class Vector {
    constructor(x, y) {
        this._x = x;
        this._y = y;
    }

    minus(vector) {
        return new Vector(this._x - vector.x, this._y - vector.y);
    }

    to(vector) {
        return new Vector(vector.x - this._x, vector.y - this._y);
    }

    dividedBy(scalar) {
        return new Vector(this._x / scalar, this._y / scalar);
    }

    removeDirectionComponent(direction) {
        let x = this.x;
        let y = this.y;
        if (direction === "N") {
            y = bound(y, 0, Number.POSITIVE_INFINITY);
        } else if (direction === "E") {
            x = bound(x, Number.NEGATIVE_INFINITY, 0);
        } else if (direction === "S") {
            y = bound(y, Number.NEGATIVE_INFINITY, 0);
        } else if (direction === "W") {
            x = bound(x, 0, Number.POSITIVE_INFINITY);
        }
        return new Vector(x, y);
    }

    get x() {
        return this._x;
    }

    get y() {
        return this._y;
    }
}

export function bound(value, min, max) {
    return Math.min(Math.max(value, min), max);
}
