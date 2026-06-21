import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import { authApi } from '@/api/auth'
import type { LoginPayload, MeResponse, UserBrief } from '@/types'

const ACCESS_KEY = 'liuying.access'
const REFRESH_KEY = 'liuying.refresh'

export const useAuthStore = defineStore('auth', () => {
  const access = ref('')
  const refresh = ref('')
  const user = ref<UserBrief | null>(null)
  const stats = ref<MeResponse['stats'] | null>(null)
  const initialized = ref(false)
  let bootstrapPromise: Promise<boolean> | null = null

  const isLogin = computed(() => !!access.value && !!user.value)

  function persist() {
    if (access.value) localStorage.setItem(ACCESS_KEY, access.value)
    else localStorage.removeItem(ACCESS_KEY)
    if (refresh.value) localStorage.setItem(REFRESH_KEY, refresh.value)
    else localStorage.removeItem(REFRESH_KEY)
  }

  function bootstrap(): Promise<boolean> {
    if (initialized.value) return Promise.resolve(isLogin.value)
    if (bootstrapPromise) return bootstrapPromise

    bootstrapPromise = (async () => {
      access.value = localStorage.getItem(ACCESS_KEY) ?? ''
      refresh.value = localStorage.getItem(REFRESH_KEY) ?? ''
      if (!access.value) return false
      return fetchMe()
    })().finally(() => {
      initialized.value = true
      bootstrapPromise = null
    })

    return bootstrapPromise
  }

  async function fetchMe(): Promise<boolean> {
    try {
      const data = await authApi.me()
      user.value = data.user
      stats.value = data.stats
      return true
    } catch {
      // 401 拦截器会先尝试刷新 token；彻底失败时会执行 logout。
      return false
    }
  }

  async function login(payload: LoginPayload) {
    const data = await authApi.login(payload)
    access.value = data.access
    refresh.value = data.refresh
    user.value = data.user
    persist()
    await fetchMe()
    initialized.value = true
  }

  async function refreshToken() {
    if (!refresh.value) throw new Error('no refresh token')
    const data = await authApi.refresh(refresh.value)
    access.value = data.access
    persist()
    return data.access
  }

  function logout() {
    access.value = ''
    refresh.value = ''
    user.value = null
    stats.value = null
    persist()
    initialized.value = true
  }

  function patchUser(partial: Partial<UserBrief>) {
    if (!user.value) return
    user.value = { ...user.value, ...partial }
  }

  return {
    access,
    refresh,
    user,
    stats,
    initialized,
    isLogin,
    bootstrap,
    fetchMe,
    login,
    refreshToken,
    logout,
    patchUser,
  }
})
