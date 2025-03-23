<template>
        <el-menu
        :style="{width: !is_close ? '230px' : '64px'}"
        :collapse = 'is_close'
        active-text-color="#ffd04b"
        background-color="#545c64"
        class="aside-container"
        default-active="2"
        text-color="#fff"
        @open="handleOpen"
        @close="handleClose"
      >
        <p class="logo-lg">{{is_close?'检测':'自杀检测'}}</p>
        <treeMenu :menuData = menuData :index = 1 />
      </el-menu>
</template>

<script setup>

import { reactive } from 'vue';
import treeMenu from './treeMenu.vue';
import {useHeaderList } from '../store/headerList.js';
import { useRouter } from 'vue-router';
import { storeToRefs } from 'pinia';

const router = useRouter();
const menuData = reactive(router.options.routes[0].children);

const HeaderList = useHeaderList();

const { is_close } = storeToRefs(HeaderList);






const handleOpen = (key, keyPath) => {
  // console.log(key, keyPath);
};

const handleClose = (key, keyPath) => {
  // console.log(key, keyPath);
};


</script>

<style lang="less" scoped>

.aside-container {
    height: 100%;
    .logo-lg {
        font-size: 15px;
        text-align: center;
        height: 50px;
        line-height: 50px;
        color: #fff;
    }
}

</style>

