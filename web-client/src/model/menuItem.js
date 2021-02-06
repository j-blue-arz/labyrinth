export default class MenuItem {
    constructor(key, text, submenu = null) {
        this.key = key;
        this.text = text;
        this._submenu = submenu;
    }

    get submenu() {
        return this._submenu;
    }

    hasSubmenu() {
        return this.submenu !== null && this.submenu.length > 0;
    }
}
