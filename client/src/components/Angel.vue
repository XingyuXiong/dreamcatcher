<template>
  <div>
    <div v-if="login">
      你好呀，{{ angel.nickname }}，积分：{{ score }}
      <button @click="logoutClicked">注销</button>
    </div>
    <div v-else>
      <router-link to="/login">登录</router-link>
    </div>
  </div>
</template>

<script>
import api from '../api'

export default {
  name: 'Angel',
  props: ['login', 'angel'],
  data() {
    return {
      score: 0,
    }
  },
  watch: {
    login(val) {
      if (!val) {
        return
      }
      api.get('angel/' + this.angel.id).then(data => {
        this.score = data.score
      })
    }
  },
  methods: {
    logoutClicked() {
      api.post('angel/logout').then(() => {
        this.$emit('logout')
      })
    },
  },
}
</script>
