import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import { adminApi } from '@/api/admin'
import type { AdminIdentity } from '@/types'

const ACCESS_KEY = 'liuying.admin.access'
const REFRESH_KEY = 'liuying.admin.refresh'

export const useAdminAuthStore = defineStore('admin-auth', () => {
  const access = ref('')
  const refresh = ref('')
  const user = ref<AdminIdentity | null>(null)
  const initialized = ref(false)
  let bootPromise: Promise<boolean> | null = null

  const isLogin = computed(() => Boolean(access.value && user.value?.is_staff))

  function persist() {
    if (access.value) localStorage.setItem(ACCESS_KEY, access.value)
    else localStorage.removeItem(ACCESS_KEY)
    if (refresh.value) localStorage.setItem(REFRESH_KEY, refresh.value)
    else localStorage.removeItem(REFRESH_KEY)
  }

  async function fetchMe() {
    try {
      user.value = await adminApi.me()
      return true
    } catch {
      return false
    }
  }

  function bootstrap(): Promise<boolean> {
    if (initialized.value) return Promise.resolve(isLogin.value)
    if (bootPromise) return bootPromise
    bootPromise = (async () => {
      access.value = localStorage.getItem(ACCESS_KEY) ?? ''
      refresh.value = localStorage.getItem(REFRESH_KEY) ?? ''
      if (!access.value) return false
      return fetchMe()
    })().finally(() => {
      initialized.value = true
      bootPromise = null
    })
    return bootPromise
  }

  async function login(payload: { account: string; password: string }) {
    const result = await adminApi.login(payload)
    access.value = result.access
    refresh.value = result.refresh
    user.value = result.user
    initialized.value = true
    persist()
  }

  async function refreshToken() {
    if (!refresh.value) throw new Error('missing refresh token')
    const result = await adminApi.refresh(refresh.value)
    access.value = result.access
    persist()
    return result.access
  }

  function logout() {
    access.value = ''
    refresh.value = ''
    user.value = null
    initialized.value = true
    persist()
  }

  return {
    access,
    refresh,
    user,
    initialized,
    isLogin,
    bootstrap,
    login,
    refreshToken,
    logout,
  }
})

