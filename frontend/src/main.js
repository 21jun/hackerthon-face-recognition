// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import router from './router'
import WebCam from "vue-web-cam";
import vuetify from 'vuetify'
import '../node_modules/vuetify/dist/vuetify.css'
import axios from 'axios'
//import 'material-design-icons-iconfont/dist/material-design-icons.css'


Vue.config.productionTip = false
Vue.use(WebCam);
Vue.use(vuetify);
Vue.use(axios)

Vue.prototype.$EventBus = new Vue();
/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  components: { App },
  template: '<App/>'
})
