import {createRouter,createWebHashHistory} from 'vue-router'
import Main from '../views/Main.vue'
import Login from '../views/login/login.vue'

import Admin from '../views/Admin/index.vue'
import Group from '../views/Group/index.vue'
import Staff from '../views/Staff/index.vue'
import Order from '../views/Order/index.vue'
import Dection from '../views/Dection/index.vue'





const routes = [
  { 
    path: '/',
    component: Main,
    name: 'main',
    children: [
      {
        path: 'dashboard',
        meta: { id: '1', name: '自杀倾向检测', icon: 'EditPen', path: '/dashboard', describe: '用于展示当前系统中的统计数据、统计报表及重要实时数据' },
        component: Dection
      },
      {
        path: 'auth',
        meta: { id: '2' ,name: '用户帖子管理', icon: 'Grid' },
        children: [
          {
            path: '',
            alias: ['admin'],
            meta: { id: '1', name: '数据管理', icon: 'Avatar', path: '/auth/admin', describe: '管理员可以进行编辑，权限修改后需要登出才会生效' },
            component: Admin
          },
          // {
          //   path: 'group',
          //   meta: { id: '2', name: '菜单管理', icon: 'Menu', path: '/auth/group', describe: '菜单规则通常对应一个控制器的方法,同时菜单栏数据也从规则中获取' },
          //   component: Group
          // }
        ]
      },
      {
        path: 'vppz',
        meta: { id: '3', name: '治疗与干预机构', path:'/vppz',icon: 'LocationInformation',describe: '陪护师可以进行创建和修改，设置对应生效状态控制C端选择'  },
        component: Staff


      },
      {
        path: 'about',
        meta: { id: '4', name: '关于我们', path:'/about',icon: 'Message',describe: '社交媒体情感分析团队'  },
        component: Group


      }
    ],
    redirect: '/dashboard'
  },
  {
    path: '/login',
    component: Login
  },
]

export default createRouter({
  history:createWebHashHistory(),
  routes:routes
})