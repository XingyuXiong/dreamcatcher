<template>
  <div>
    <p>名字：{{ angel.registered_name }}</p>
    <p>学号：{{ angel.registered_id }}</p>
    <input type="text" v-model="nickname" :placeholder="angel.registered_name">
    <button @click="angelConfirmed">确定</button>
  </div>
</template>

<script>
import api from '../api'

export default {
  props: ['angel'],
  data() {
    return {
      nickname: ''
    }
  },
  methods: {
    angelConfirmed() {
      api.post('angel/update', {
        'nickname': this.nickname
      }).then(() => {
        this.$router.push({ name: 'home' })
      })
    }
  }
}
</script>
