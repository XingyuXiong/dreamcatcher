<template>
  <div>
    <a v-if="casLink != null" :href="casLink">跳转至CAS登录</a>
    <create-angel v-else-if="createAngel" :angel="angel"></create-angel>
    <div v-else>等一下哦……</div>
  </div>
</template>

<script>
import api from '../api'
import CreateAngel from './CreateAngel'

export default {
  components: {
    CreateAngel,
  },
  data() {
    return {
      ticket: null,
      casLink: null,
      angel: null,
      createAngel: false,
    }
  },
  created() {
    // https://stackoverflow.com/a/901144
    const urlParams = new URLSearchParams(window.location.search)
    this.ticket = urlParams.get('ticket')
    
    const postData = { 'back': window.location.href }
    if (this.ticket) {
      postData['ticket'] = this.ticket
    }

    api.post('angel/login', postData).then(data => {
      if (data.ticket_required) {
        this.casLink = data.redirect_url
      } else {
        if (data.exist) {
          this.$router.push({ name: 'home', query: null })
        } else {
          this.angel = data.angel
          this.createAngel = true
        }
      }
    })
  }
}
</script>
