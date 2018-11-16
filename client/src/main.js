import Vue from 'vue'
import VueRouter from 'vue-router'

Vue.use(VueRouter)

import App from './App.vue'
import Home from './components/Home'
import Login from './components/Login'
import CreateTask from './components/CreateTask'
import Task from './components/Task'

Vue.config.productionTip = false

const router = new VueRouter({
  mode: 'history',
  routes: [
    { path: '', component: Home, name: 'home' },
    { path: '/login', component: Login, name: 'login' },  
    { path: '/task/new', component: CreateTask, name: 'createTask' },
    { path: '/task/:taskID', component: Task, name: 'task' },
  ],
})

window.config = {
  API_ROOT: 'http://localhost:8000/',
}

new Vue({
  render: h => h(App),
  router,
}).$mount('#app')
