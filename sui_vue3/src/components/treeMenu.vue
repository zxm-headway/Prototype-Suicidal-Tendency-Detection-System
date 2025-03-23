<template>
  <template v-for="(item) in props.menuData">
    <el-menu-item 
      
      @click="handleClick(item,`${props.index}-${item.meta.id}`)"
      v-if="!item.children || item.children.length === 0" :index="`${props.index}-${item.meta.id}`" :key="`${props.index}-${item.meta.id}`">
      <el-icon size="20">
        <component :is="item.meta.icon" />
      </el-icon>
        <span>{{item.meta.name}}</span>
      </el-menu-item>
      <el-sub-menu v-else  :index="`${props.index}-${item.meta.id}`" >
        <template #title>
          <el-icon size="20">
            <component :is="item.meta.icon" />
          </el-icon>
          <span>{{item.meta.name}}</span>
        </template>
        <treeMenu :menuData="item.children" :index="`${props.index}-${item.meta.id}`" />
      </el-sub-menu>

  </template>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router';
import {storeToRefs } from 'pinia'

import {useHeaderList} from '../store/headerList.js'
import { fr } from 'element-plus/es/locales.mjs';

const HeaderList = useHeaderList()

const { getHeaderListLen } = storeToRefs(HeaderList)


const router = useRouter();
const handleClick = (item,index) => {
  router.push(item.meta.path)
  HeaderList.addHeaderList(item)
  // console.log(getHeaderListLen.value,'getHeaderListLen')


}



const props = defineProps(['menuData','index']);
// console.log(props,'props')

</script>

<style lang="less" scoped> 
</style>