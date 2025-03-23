<template>
  <div class="common-layout">
    <el-container>
      <Aside />
      <el-container>
        <el-header>
          <Header />
        </el-header>
        <el-main>
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
// import { ref } from 'vue'
import Aside from '../components/aside.vue';
import Header from '../components/header.vue';


</script>

<style lang="less" scoped>
.common-layout {
  height: 100%;
  .el-container {
    height: 100%;
    // .el-header {
    //   background-color: #b3c0d1;
    //   line-height: 60px;
    // }
    // .el-aside {
    //   background-color: #545c64;
    //   color: #fff;
    //   line-height: 200px;
    // }
    // .el-main {
    //   background-color: #e9ecf3;
    //   color: #333;
    //   line-height: 200px;
    // }
  }
}
</style>
