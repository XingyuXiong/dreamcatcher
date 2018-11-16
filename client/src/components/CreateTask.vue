<template>
  <div>
    <p>任务描述</p>
    <textarea v-model="description"></textarea>
    <p>支付金额<input type="text" v-model="cost"></p>
    <p>{{ pointDescription }}</p>
    <button @click="payForTask">支付</button>
    <button @click="submitTask" :disabled="!submitButtonEnable">提交任务</button>
  </div>
</template>

<script>
import api from '../api'

export default {
  data() {
    return {
      pointDescription: '稍等一下',
      cost: 0.2,
      description: '',
      paid: false,
      point: 0,
    }
  },
  computed: {
    submitButtonEnable() {
      return this.paid && this.description != ''
    }
  },
  created() {
    this.updatePoint()
  },
  watch: {
    cost() {
      // TODO: throttle
      this.updatePoint()
    }
  },
  methods: {
    updatePoint() {
      if (this.cost == '') {
        return
      }
      // TODO: check this.cost is float
      this.pointDescription = '稍等一下'
      api.get('task/point', {cost: parseFloat(this.cost)}).then(data => {
        this.pointDescription = '完成该任务可获得' + data.point + '点积分'
        this.point = data.point
      })
    },
    payForTask() {
      alert('你支付了' + this.cost + '元哦！')
      this.paid = true
    },
    submitTask() {
      api.post('task/', {
        description: this.description,
        cost: parseFloat(this.cost),
      }).then(data => {
        this.$router.push({ name: 'task', params: { taskID: data.id } })
      })
    }
  }
}
</script>
