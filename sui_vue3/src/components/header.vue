<template>
  <div class="header-container ">

    <div class="header-left flex-box">
      <el-icon class="icon" @click="HeaderList.closeHeader" v-if="!is_close"><Fold /></el-icon>
      <el-icon v-else class="icon" @click="HeaderList.closeHeader" ><Expand /></el-icon>

      <ul class="flex-box">
        <li v-for="(item) in header_list" :key="item.path" class="flex-box tab"  :class="{selected:route.path== item.path}">
            <el-icon size="12" class="icon">
                <component :is="item.icon" />
            </el-icon>
            <router-link :to="item.path" class=" flex-box">{{item.name}}</router-link>
            <el-icon size="13" class="icon close" @click="remove_breradcrumb (item.path)"><Close/></el-icon>
        </li>
      </ul>


    </div >

    <div class = "header-right flex-box">
      <div class="user-name">
        <el-avatar src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png"/>
      </div>
      <!-- <div >{{HeaderList.header_list}}</div> -->
      <el-dropdown placement="bottom-end">
      <el-button> 个人中心 </el-button>
      <template #dropdown>
        <el-dropdown-menu>

          <el-dropdown-item>修改信息</el-dropdown-item>
          <el-dropdown-item @click="go_out">退出登录</el-dropdown-item>
          <!-- <el-dropdown-item></el-dropdown-item> -->
        </el-dropdown-menu>
      </template>
    </el-dropdown>
      
    </div>


  </div>
  
</template>

<script setup>

import {useHeaderList} from  '../store/headerList.js'
import {storeToRefs } from 'pinia'

import { useRoute,useRouter } from 'vue-router'; 

const route = useRoute()
const router = useRouter()
const HeaderList = useHeaderList()
const { is_close, header_list,getHeaderListLen} = storeToRefs(HeaderList)

const go_out = () => {
    router.push('/login')
}

const remove_breradcrumb = (path) => {
    const index =  HeaderList.removeHeaderList(path)
    if(route.path != path){
        return
    }

    if(index == getHeaderListLen.value){
        if(getHeaderListLen.value == 0){
            router.push('/')
        }else{
            router.push(HeaderList.header_list[index-1].path)
        }
    }
    else{
        router.push(HeaderList.header_list[index].path)
    }
}


</script>

<style lang='less' scoped>
.flex-box {
    display: flex;
    align-items: center;
    height: 100%;
}

.header-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 100%;
    background-color: #fff;
    padding-right: 25px;
    .header-left {
        height: 100%;
        .icon {
            width: 45px;
            height: 100%;
        }
        .icon:hover {
            background-color: #f5f5f5;
            cursor: pointer;
        }
        .tab {
            padding: 0 5px;
            height: 100%;
            .text {
                margin: 0 5px;
            }
            .close {
                visibility: hidden;
            }
            &.selected {
                a {
                    color: #409eff;
                }
                i {
                    color: #409eff;
                }
                background-color: #f5f5f5;
            }
        }
        .tab:hover {
            background-color: #f5f5f5;
            .close {
                visibility: inherit;
                cursor: pointer;
                color: #000;
            }
        }
    }
    .header-right {
        .user-name {
            margin-left: 10px;
        }
    }
    a {
        height: 100%;
        color: #333;
        font-size: 15px;
    }
}

</style>