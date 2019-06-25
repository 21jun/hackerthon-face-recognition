import Vue from 'vue'
import Router from 'vue-router'
import HelloWorld from '@/components/HelloWorld'
import RegistPage from '@/components/RegistPage'
import DetectPage from '@/components/DetectPage'
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
    }
  ]
})
