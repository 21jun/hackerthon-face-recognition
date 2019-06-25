import Vue from 'vue'
import Router from 'vue-router'
import HelloWorld from '@/components/HelloWorld'
import DetectPage from '@/components/DetectPage'
import UserStatics from '@/components/UserStatics'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'HelloWorld',
      component: HelloWorld
    },
    {
      path: '/DetectPage',
      name: 'DetectPage',
      component: DetectPage
    },
    {
      path: '/UserStatics',
      name: 'UserStatics',
      component: UserStatics
    }
  ]
})
