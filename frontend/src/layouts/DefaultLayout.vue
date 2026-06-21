<script setup lang="ts">
import { computed, ref } from 'vue'
import { RouterLink, RouterView, useRouter } from 'vue-router'
import { Bell, EditPen, Menu, Search, User } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const query = ref('')
const mobileOpen = ref(false)
const userAvatar = computed(() => auth.user?.avatar || '/default-avatar.svg')

function submitSearch() {
  const q = query.value.trim()
  if (!q) return
  router.push({ name: 'search', query: { q } })
  mobileOpen.value = false
}
function onLogout() {
  auth.logout()
  ElMessage.success('已退出登录')
  router.push({ name: 'home' })
}
</script>

<template>
  <div class="site-shell">
    <header class="topbar">
      <div class="topbar-inner">
        <button class="menu-button" type="button" aria-label="打开菜单" @click="mobileOpen = !mobileOpen"><el-icon><Menu /></el-icon></button>
        <RouterLink :to="{ name: 'home' }" class="brand">
          <span class="brand-mark">LY</span><span class="brand-name">流萤社区</span>
        </RouterLink>
        <form class="top-search" @submit.prevent="submitSearch">
          <el-icon><Search /></el-icon>
          <input v-model="query" placeholder="搜索技术文章、作者或关键词" />
          <button type="submit">搜索</button>
        </form>
        <div class="top-actions">
          <button class="icon-action" type="button" title="消息"><el-icon><Bell /></el-icon></button>
          <template v-if="auth.isLogin">
            <el-dropdown trigger="click">
              <button type="button" class="account-button"><img :src="userAvatar" alt="" /><span>{{ auth.user?.username }}</span></button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="router.push({ name: 'profile' })">个人中心</el-dropdown-item>
                  <el-dropdown-item divided @click="onLogout">退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
          <button v-else class="login-button" type="button" @click="router.push({ name: 'login' })"><el-icon><User /></el-icon>登录</button>
          <button class="create-button" type="button" @click="router.push({ name: 'pub-blog' })"><el-icon><EditPen /></el-icon>创作</button>
        </div>
      </div>
      <div v-if="mobileOpen" class="mobile-menu">
        <RouterLink :to="{ name: 'home' }" @click="mobileOpen = false">首页</RouterLink>
        <RouterLink :to="{ name: 'pub-blog' }" @click="mobileOpen = false">发布博客</RouterLink>
        <RouterLink v-if="auth.isLogin" :to="{ name: 'profile' }" @click="mobileOpen = false">个人中心</RouterLink>
        <RouterLink v-else :to="{ name: 'register' }" @click="mobileOpen = false">注册账号</RouterLink>
      </div>
    </header>

    <main class="app-main"><RouterView /></main>

    <footer class="app-footer">
      <span>© 2026 流萤社区</span><span>让知识保持流动，让灵感持续发光</span>
    </footer>
  </div>
</template>

<style scoped>
.site-shell { min-height: 100vh; }
.topbar { position: sticky; top: 0; z-index: 50; border-bottom: 1px solid var(--silver-200); background: rgba(255,255,255,.97); backdrop-filter: blur(12px); }
.topbar-inner { display: grid; grid-template-columns: auto auto minmax(260px,680px) 1fr; align-items: center; gap: 18px; min-height: 64px; padding: 0 24px; }
.menu-button,.icon-action { display: grid; width: 38px; height: 38px; place-items: center; border: 0; border-radius: 8px; background: transparent; cursor: pointer; font-size: 1.25rem; }
.menu-button:hover,.icon-action:hover { background: var(--silver-100); color: var(--cyan-700); }
.brand { display: flex; align-items: center; gap: 10px; white-space: nowrap; }
.brand-mark { display: grid; width: 36px; height: 36px; place-items: center; border-radius: 10px; background: var(--cyan-600); color: #fff; font-size: .78rem; font-weight: 800; box-shadow: 0 6px 16px rgba(7,150,165,.22); }
.brand-name { font-size: 1.15rem; font-weight: 800; letter-spacing: -.03em; }
.top-search { display: flex; align-items: center; height: 42px; margin-left: 18px; overflow: hidden; border: 1px solid var(--silver-200); border-radius: 10px; background: var(--silver-50); color: var(--silver-500); }
.top-search > .el-icon { margin-left: 14px; }
.top-search input { flex: 1; min-width: 0; padding: 0 12px; border: 0; outline: none; background: transparent; color: var(--silver-900); }
.top-search button { align-self: stretch; padding: 0 24px; border: 0; background: var(--cyan-600); color: #fff; cursor: pointer; font-weight: 700; }
.top-search:focus-within { border-color: var(--cyan-500); box-shadow: 0 0 0 3px var(--cyan-100); }
.top-actions { display: flex; align-items: center; justify-content: flex-end; gap: 10px; }
.login-button,.create-button,.account-button { display: flex; align-items: center; gap: 7px; height: 38px; padding: 0 14px; border-radius: 9px; cursor: pointer; font-weight: 700; }
.login-button,.account-button { border: 1px solid var(--silver-200); background: #fff; }
.create-button { border: 0; background: var(--cyan-600); color: #fff; }
.create-button:hover { background: var(--cyan-700); }
.account-button img { width: 26px; height: 26px; border-radius: 50%; object-fit: cover; }
.mobile-menu { display: none; }
.app-main { min-height: calc(100vh - 112px); }
.app-footer { display: flex; justify-content: center; gap: 24px; padding: 18px; border-top: 1px solid var(--silver-200); background: #fff; color: var(--silver-500); font-size: .76rem; }
@media (max-width: 1080px) {
  .topbar-inner { grid-template-columns: auto auto 1fr auto; }
  .brand-name,.icon-action,.login-button span { display: none; }
  .top-search { margin-left: 0; }
}
@media (max-width: 720px) {
  .topbar-inner { grid-template-columns: auto auto 1fr auto; gap: 8px; min-height: 58px; padding: 0 12px; }
  .top-search { height: 38px; }
  .top-search button { display: none; }
  .create-button { width: 38px; padding: 0; justify-content: center; }
  .create-button { font-size: 0; }
  .create-button .el-icon { font-size: 1rem; }
  .mobile-menu { display: grid; padding: 8px 12px 14px; border-top: 1px solid var(--silver-100); }
  .mobile-menu a { padding: 12px; border-radius: 8px; font-weight: 700; }
  .mobile-menu a:hover { background: var(--cyan-50); color: var(--cyan-700); }
  .app-footer { flex-direction: column; align-items: center; gap: 4px; }
}
</style>
