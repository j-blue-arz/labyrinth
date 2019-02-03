export default class MenuItem {
    constructor(key, text, submenu = null) {
        this.key = key;
        this.text = text;
        this.submenu = submenu;
    }

    hasSubmenu() {
        return this.submenu !== null && this.submenu.length > 0;
    }
}
