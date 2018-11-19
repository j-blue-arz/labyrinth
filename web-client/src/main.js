import Vue from "vue";
import App from "@/components/App.vue";

Vue.config.productionTip = false;

new Vue({
    render: function(h) {
        return h(App);
    }
}).$mount("#app");
