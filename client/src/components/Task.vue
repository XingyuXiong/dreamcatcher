<template>
  <div>
    <div v-if="!loading">
      <p>{{ task.description }}</p>
      <div v-if="!isOwner">
        <p>发起人：{{ owner.nickname }}（{{ owner.registered_name }}）</p>
        <p>完成后可以得到{{ task.point }}点积分哦</p>
      </div>
      <div v-if="status == 'waiting'">
        <div v-if="!isOwner">
          <button @click="acceptTask">接下这个任务！</button>      
        </div>
        <div v-else>等待好心人中……</div>
      </div>              
      <div v-else-if="status == 'processing'">
        <div v-if="!isHelper">
          <p>帮助者：{{ helper.nickname }}</p>
        </div>
        <div v-if="isOwner">
          <button disabled="disabled">给ta发消息（然而并不能）</button>
          <button @click="finishTask">任务已经完成啦！</button>                    
        </div>
        <div v-if="isHelper">
          <button disabled="disabled">给ta发消息（然而并不能）</button>        
        </div>
      </div>
      <div v-else>
        <p>已完成</p>
        <div v-if="!isHelper">
          <p>帮助者：{{ helper.nickname }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../api'

export default {
  data() {
    return {
      loading: true,
      task: null,
      owner: null,
      helper: null,
      isHelper: null,
      isOwner: null,
      taskID: this.$route.params.taskID,   
      status: null,   
    }
  },
  created() {
    this.updateTask()
  },
  methods: {
    acceptTask() {
      api.post('task/' + this.taskID + '/accept').then(data => {
        this.updateTask() 
      })
    },
    finishTask() {
      api.post('task/' + this.taskID + '/finish').then(data => {
        this.updateTask()
      })
    },
    updateTask() {
      api.get('task/' + this.taskID).then(data => {
        this.task = data
        api.get('angel/info').then(data => {
          const angel = data.angel
          api.get('angel/' + this.task.owner_id).then(data => {
            this.owner = data
            this.isOwner = angel.id == this.task.owner_id
            if (this.task.helper_id == null) {
              this.isHelper = false
              this.status = 'waiting'
              this.loading = false
            } else {
              this.isHelper = angel.id == this.task.helper_id
              this.status = this.task.is_finished ? 'finished' : 'processing'
              api.get('angel/' + this.task.helper_id).then(data => {
                this.helper = data
                this.loading = false
              })
            }
          })
        })
      })
    }
  }
}
</script>
