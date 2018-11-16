<template>
  <div>
    <div v-if="login">
      你好呀，{{ angel.nickname }}<button @click="logoutClicked">注销</button>
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
  methods: {
    logoutClicked() {
      api.post('angel/logout').then(() => {
        this.$emit('logout')
      })
    },
  },
}
</script>
