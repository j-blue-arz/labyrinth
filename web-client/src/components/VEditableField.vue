<template>
    <p>
        <span @click="startEditing" v-show="!editing">{{ content }}</span>
        <span v-show="editing">
            <input v-model="text" @blur="stopEditing" type="text" />
        </span>
    </p>
</template>

<script>
export default {
    name: "v-editable-field",
    data() {
        return {
            text: "",
            editing: false
        };
    },
    props: {
        placeholder: {
            type: String,
            default: ""
        }
    },
    computed: {
        content: function() {
            if (this.text === "") {
                return this.placeholder;
            } else {
                return this.text;
            }
        }
    },
    methods: {
        startEditing: function() {
            this.editing = true;
        },
        stopEditing: function() {
            this.editing = false;
        }
    }
};
</script>

<style lang="scss"></style>
