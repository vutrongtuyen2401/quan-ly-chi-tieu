import axios from 'axios'
import { useSessionStore } from './stores/session'

// Axios dùng chung cho mọi store. Đường dẫn /api/... được Vite proxy sang backend (vite.config.js).
const api = axios.create({ baseURL: '' })

api.interceptors.request.use(config => {
  const session = useSessionStore()
  if (session.token) config.headers.Authorization = `Bearer ${session.token}`
  return config
})

// Token hết hạn / tài khoản bị khóa → tự đăng xuất thay vì để các request thất bại âm thầm
api.interceptors.response.use(
  response => response,
  error => {
    const session = useSessionStore()
    const isAuthCall = (error.config?.url || '').startsWith('/api/auth/')
    if (error.response?.status === 401 && !isAuthCall && session.isLoggedIn) {
      const reason = error.response.data?.detail || 'Phiên đăng nhập đã hết hạn.'
      session.doLogout()
      session.errorMsg = reason
      session.showToast(`🔒 ${reason}`, 'error')
    }
    return Promise.reject(error)
  }
)

export default api
