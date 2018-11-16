<template>
  <div v-if="!login">
    登录以后可以查看任务列表哦
  </div>
  <div v-else-if="loading">
    稍等一下哦
  </div>
  <div v-else>
    <p>我的任务</p>
    <div v-if="ownedUnfinishedTask != null">
      <router-link :to="{ name: 'task', params: { taskID: ownedUnfinishedTask.id }}">
        {{ ownedUnfinishedTask.description }}
      </router-link>
    </div>
    <router-link v-else :to="{ name: 'createTask' }">创建任务</router-link>

    <p>我接受的任务</p>
    <div v-for="task in acceptedTasks" :key="task.id">
      <router-link :to="{ name: 'task', params: { taskID: task.id }}">
        {{ task.description }}
      </router-link>
    </div>

    <p>可以接受的任务</p>
    <div v-for="task in otherTasks" :key="task.id">
      <router-link :to="{ name: 'task', params: { taskID: task.id }}">
        {{ task.description }}
      </router-link>      
    </div>
  </div>
</template>

<script>
import api from '../api'

export default {
  props: ['login'],
  data() {
    return {
      loading: true,
      ownedUnfinishedTask: null,
      acceptedTasks: null,
      otherTasks: null,
    }
  },
  created() {
    this.updateTask()
  },
  watch: {
    login() {
      this.updateTask()
    }
  },
  methods: {
    updateTask() {
      if (!this.login) {
        return
      }
      api.get('task').then(data => {
        if (data.owned != null) {
          api.get('task/' + data.owned).then(data => {
            this.ownedUnfinishedTask = data        
          })        
        }
        this.acceptedTasks = []
        data.accepted.forEach(taskID => {
          api.get('task/' + taskID).then(data => {
            this.acceptedTasks.push(data)
          })
        })
        this.otherTasks = []
        data.available.forEach(taskID => {
          api.get('task/' + taskID).then(data => {
            this.otherTasks.push(data)
          })
        })
        // TODO: wait until all async fetching finish
        this.loading = false
      })
    }
  }
}
</script>
