<template>
  <angel :login="login" :angel="angel" @logout="onLogout"></angel>
</template>

<script>
import Angel from './Angel'
import api from '../api'

export default {
  name: 'Home',
  components: {
    Angel,
  },
  data() {
    return {
      login: false,
      angel: null,      
    }
  },
  created() {
    api.get('angel/info').then(data => {
      if (!data.login_required) {
        this.login = true
        this.angel = data.angel
      }
    })      
  },
  methods: {
    onLogout() {
      this.login = false
      this.angel = null
    }
  }
}

</script>
