// 主厨后台（厨房管理、博客写作台）的请求：自动带 X-Chef-Token（Authorization 留给站点 JWT），
// 并在页面加载时向后端确认令牌仍然有效
import axios from 'axios'
import { useRouter } from 'vue-router'
import API_BASE_URL from '../config/api'
import { useAuthStore } from '../store/auth'

const chefToken = () => localStorage.getItem('chef_token') || ''

export const chefHeaders = () => ({ 'X-Chef-Token': chefToken() })

// 主厨页面统一用这个实例，写操作和 ?mode=chef 的读都需要主厨令牌
export const chefApi = axios.create()
chefApi.interceptors.request.use((config) => {
  config.headers['X-Chef-Token'] = chefToken()
  return config
})

export function useChefGuard() {
  const router = useRouter()
  const authStore = useAuthStore()

  // 旧版或过期令牌：退出主厨登录，登录后回到当前页。
  // 用不带拦截器的 axios，避免 401 触发站点 JWT 的刷新与跳转
  const ensureChef = async () => {
    try {
      await axios.get(`${API_BASE_URL}/api/chef/login/`, { headers: chefHeaders() })
      return true
    } catch (e) {
      authStore.chefLogout()
      router.replace({ path: '/kitchen/chef/login', query: { redirect: router.currentRoute.value.fullPath } })
      return false
    }
  }

  return { ensureChef }
}
