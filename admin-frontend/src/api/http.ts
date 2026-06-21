import axios, { AxiosError, type AxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'

import { useAdminAuthStore } from '@/stores/auth'

const http = axios.create({ baseURL: '/api', timeout: 30_000 })

http.interceptors.request.use((config) => {
  const auth = useAdminAuthStore()
  if (auth.access) {
    config.headers = config.headers ?? {}
    config.headers.Authorization = `Bearer ${auth.access}`
  }
  return config
})

let refreshing: Promise<string> | null = null

function errorMessage(data: unknown) {
  if (!data || typeof data !== 'object') return ''
  const record = data as Record<string, unknown>
  if (record.detail) return String(record.detail)
  return Object.values(record)
    .flatMap((value) => Array.isArray(value) ? value : [value])
    .filter(Boolean)
    .map(String)
    .join('；')
}

http.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const auth = useAdminAuthStore()
    const original = error.config as (AxiosRequestConfig & { _retry?: boolean }) | undefined

    if (error.response?.status === 401 && auth.refresh && original && !original._retry) {
      original._retry = true
      try {
        refreshing = refreshing ?? auth.refreshToken()
        const token = await refreshing
        original.headers = original.headers ?? {}
        original.headers.Authorization = `Bearer ${token}`
        return http.request(original)
      } catch {
        auth.logout()
        ElMessage.warning('管理会话已失效，请重新登录')
        window.location.href = `${import.meta.env.BASE_URL}login`
      } finally {
        refreshing = null
      }
    }

    const message = errorMessage(error.response?.data)
    if (message) ElMessage.error(message)
    return Promise.reject(error)
  },
)

export default http

