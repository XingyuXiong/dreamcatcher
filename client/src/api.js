import axios from 'axios'
import Cookies from 'js-cookie'

function get(path, data) {
  const api_root = window.config.API_ROOT
  const config = {
    withCredentials: true
  }
  if (data) {
    config['params'] = { data: JSON.stringify(data) }
  }
  return _trimmed(axios.get(api_root + path, config))
}

function post(path, data) {
  var csrftoken = Cookies.get('csrftoken');

  const api_root = window.config.API_ROOT
  return _trimmed(axios.post(api_root + path, data || {}, {
    headers: {'X-CSRFToken': csrftoken},
    withCredentials: true,
  }))
}

function _trimmed(resp) {
  return resp.then(resp => {
    if (resp.status != 200) {
      throw Error(resp.statusText)
    }

    if (resp.data.success) {
      return resp.data.data
    } else {
      throw Error(resp.data.message)
    }
  })
}

export default {
  get, post
}
