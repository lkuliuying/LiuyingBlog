import axios, { AxiosError, type AxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'

import { useAuthStore } from '@/stores/auth'

// 业务里所有的 baseURL 都指 /api（开发期被 vite 代理到 8000）
const http = axios.create({ baseURL: '/api', timeout: 30_000 })

http.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.access) {
    config.headers = config.headers ?? {}
    config.headers.Authorization = `Bearer ${auth.access}`
  }
  return config
})

let refreshing: Promise<string> | null = null

http.interceptors.response.use(
  (resp) => resp,
  async (error: AxiosError<any>) => {
    const auth = useAuthStore()
    const original = error.config as (AxiosRequestConfig & { _retry?: boolean }) | undefined
    const status = error.response?.status

    // 401 且有 refresh token：尝试自动续期一次
    if (status === 401 && auth.refresh && original && !original._retry) {
      original._retry = true
      try {
        refreshing = refreshing ?? auth.refreshToken()
        const newAccess = await refreshing
        original.headers = original.headers ?? {}
        original.headers.Authorization = `Bearer ${newAccess}`
        return http.request(original)
      } catch {
        auth.logout()
        ElMessage.warning('登录已过期，请重新登录')
        if (typeof window !== 'undefined') {
          window.location.href = '/login'
        }
      } finally {
        refreshing = null
      }
    }

    // 提取后端给的提示
    const data = error.response?.data
    if (data && typeof data === 'object') {
      const detail = (data as any).detail
        ?? Object.values(data).flat().filter(Boolean).join('；')
      if (detail) ElMessage.error(String(detail))
    }
    return Promise.reject(error)
  },
)

export default http
