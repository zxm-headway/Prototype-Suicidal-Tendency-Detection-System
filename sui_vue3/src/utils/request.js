import axios from 'axios'

// 创建axios实例
const service = axios.create({
  baseURL:'/api', // 使用 Vite 代理配置的路径
  timeout: 5000 // 请求超时时间
})

// request拦截器
service.interceptors.request.use(
  config => {
    // 在请求发送之前做一些处理
    return config
  },
  error => {
    // 处理请求错误
    console.log(error) // for debug
    return Promise.reject(error)
  }
)

// response拦截器
service.interceptors.response.use(
  response => {
    // 在这里对返回的数据进行处理
    return response
  },
  error => {
    // 处理响应错误
    console.log('err' + error) // for debug
    return Promise.reject(error)
  }
)

export default service