<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  ArrowDown,
  ChatDotRound,
  DataBoard,
  Document,
  Expand,
  Fold,
  FolderOpened,
  Link,
  SwitchButton,
  User,
} from '@element-plus/icons-vue'
import { ElMessageBox } from 'element-plus'

import { useAdminAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAdminAuthStore()
const collapsed = ref(false)
const mobileOpen = ref(false)

const currentPath = computed(() => route.path)
const avatarLetter = computed(() => auth.user?.username?.slice(0, 1).toUpperCase() || 'A')

const navItems = [
  { path: '/', label: '工作台', hint: 'Overview', icon: DataBoard },
  { path: '/blogs', label: '博客管理', hint: 'Articles', icon: Document },
  { path: '/categories', label: '分类管理', hint: 'Taxonomy', icon: FolderOpened },
  { path: '/comments', label: '评论管理', hint: 'Moderation', icon: ChatDotRound },
  { path: '/users', label: '用户管理', hint: 'Community', icon: User },
]

function navigate(path: string) {
  mobileOpen.value = false
  router.push(path)
}

async function logout() {
  await ElMessageBox.confirm('确定退出管理后台吗？', '退出登录', {
    confirmButtonText: '退出',
    cancelButtonText: '取消',
    type: 'warning',
  })
  auth.logout()
  router.replace({ name: 'admin-login' })
}
</script>

<template>
  <div class="admin-shell" :class="{ collapsed }">
    <div v-if="mobileOpen" class="mobile-mask" @click="mobileOpen = false" />
    <aside class="sidebar" :class="{ 'mobile-open': mobileOpen }">
      <button class="brand" type="button" @click="navigate('/')">
        <span class="brand-mark">LY</span>
        <span class="brand-copy">
          <strong>流萤管理台</strong>
          <small>COMMUNITY OS</small>
        </span>
      </button>

      <div class="workspace-chip">
        <span class="status-dot" />
        <span class="brand-copy">
          <strong>社区内容中心</strong>
          <small>服务运行中</small>
        </span>
      </div>

      <nav class="main-nav" aria-label="管理后台导航">
        <button
          v-for="item in navItems"
          :key="item.path"
          type="button"
          class="nav-item"
          :class="{ active: currentPath === item.path }"
          @click="navigate(item.path)"
        >
          <el-icon><component :is="item.icon" /></el-icon>
          <span class="nav-copy"><strong>{{ item.label }}</strong><small>{{ item.hint }}</small></span>
          <span class="nav-line" />
        </button>
      </nav>

      <div class="sidebar-foot">
        <a class="site-link" href="/" target="_blank">
          <el-icon><Link /></el-icon>
          <span>访问社区前台</span>
        </a>
        <button class="collapse-button" type="button" @click="collapsed = !collapsed">
          <el-icon><component :is="collapsed ? Expand : Fold" /></el-icon>
          <span>{{ collapsed ? '展开导航' : '收起导航' }}</span>
        </button>
      </div>
    </aside>

    <section class="main-shell">
      <header class="topbar">
        <button class="mobile-menu" type="button" aria-label="打开导航" @click="mobileOpen = true">
          <el-icon><Expand /></el-icon>
        </button>
        <div class="breadcrumb">
          <span>流萤社区</span>
          <i>/</i>
          <strong>{{ route.meta.title || navItems.find((item) => item.path === currentPath)?.label || '管理后台' }}</strong>
        </div>
        <div class="top-actions">
          <span class="environment"><i />Production</span>
          <el-dropdown trigger="click">
            <button class="account-button" type="button">
              <el-avatar :size="34" :src="auth.user?.avatar">{{ avatarLetter }}</el-avatar>
              <span class="account-copy">
                <strong>{{ auth.user?.username }}</strong>
                <small>{{ auth.user?.is_superuser ? '超级管理员' : '内容管理员' }}</small>
              </span>
              <el-icon><ArrowDown /></el-icon>
            </button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item disabled>{{ auth.user?.email || '未设置邮箱' }}</el-dropdown-item>
                <el-dropdown-item divided @click="logout">
                  <el-icon><SwitchButton /></el-icon>退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <main class="content">
        <RouterView v-slot="{ Component }">
          <Transition name="page" mode="out-in">
            <component :is="Component" />
          </Transition>
        </RouterView>
      </main>
    </section>
  </div>
</template>

<style scoped>
.admin-shell { min-height: 100vh; }
.sidebar {
  position: fixed;
  inset: 0 auto 0 0;
  z-index: 40;
  display: flex;
  width: var(--sidebar-width);
  flex-direction: column;
  padding: 18px 14px;
  overflow: hidden;
  border-right: 1px solid rgba(255,255,255,.08);
  background:
    radial-gradient(circle at 0 0, rgba(18,173,186,.2), transparent 34%),
    linear-gradient(165deg, #17282e 0%, #101d22 100%);
  color: #dbe7e9;
  transition: width .24s ease, transform .24s ease;
}
.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 6px 8px 20px;
  border: 0;
  background: transparent;
  color: #fff;
  cursor: pointer;
  text-align: left;
}
.brand-mark {
  display: grid;
  width: 42px;
  height: 42px;
  flex: none;
  place-items: center;
  border: 1px solid rgba(255,255,255,.22);
  border-radius: 13px;
  background: linear-gradient(135deg, var(--cyan-500), var(--cyan-700));
  box-shadow: 0 10px 28px rgba(7,150,165,.26);
  font-size: 12px;
  font-weight: 900;
  letter-spacing: .08em;
}
.brand-copy { display: grid; min-width: 0; }
.brand-copy strong { overflow: hidden; font-size: 14px; text-overflow: ellipsis; white-space: nowrap; }
.brand-copy small { margin-top: 3px; color: #7f999f; font-size: 9px; font-weight: 800; letter-spacing: .16em; }
.workspace-chip {
  display: flex;
  align-items: center;
  gap: 11px;
  margin: 0 4px 20px;
  padding: 12px;
  border: 1px solid rgba(255,255,255,.08);
  border-radius: 12px;
  background: rgba(255,255,255,.04);
}
.workspace-chip .brand-copy strong { font-size: 12px; }
.workspace-chip .brand-copy small { color: #789197; letter-spacing: 0; }
.status-dot { width: 8px; height: 8px; flex: none; border-radius: 50%; background: #62d6a5; box-shadow: 0 0 0 5px rgba(98,214,165,.1); }
.main-nav { display: grid; gap: 5px; }
.nav-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 12px;
  min-height: 54px;
  padding: 8px 12px;
  overflow: hidden;
  border: 0;
  border-radius: 11px;
  background: transparent;
  color: #8da2a7;
  cursor: pointer;
  text-align: left;
  transition: color .18s ease, background .18s ease;
}
.nav-item > .el-icon { flex: none; font-size: 18px; }
.nav-copy { display: grid; min-width: 0; }
.nav-copy strong { font-size: 13px; }
.nav-copy small { margin-top: 2px; color: #5f767c; font-size: 9px; letter-spacing: .1em; text-transform: uppercase; }
.nav-item:hover { color: #e9f5f6; background: rgba(255,255,255,.045); }
.nav-item.active { color: #fff; background: linear-gradient(90deg, rgba(18,173,186,.2), rgba(18,173,186,.07)); }
.nav-item.active .nav-copy small { color: #71cbd2; }
.nav-line { position: absolute; inset: 11px 0 11px auto; width: 3px; border-radius: 4px 0 0 4px; background: var(--cyan-500); opacity: 0; }
.nav-item.active .nav-line { opacity: 1; }
.sidebar-foot { display: grid; gap: 5px; margin-top: auto; }
.site-link,.collapse-button {
  display: flex;
  align-items: center;
  gap: 12px;
  min-height: 42px;
  padding: 0 12px;
  border: 0;
  border-radius: 10px;
  background: transparent;
  color: #789197;
  cursor: pointer;
  font-size: 12px;
}
.site-link:hover,.collapse-button:hover { color: #fff; background: rgba(255,255,255,.05); }
.main-shell { min-height: 100vh; margin-left: var(--sidebar-width); transition: margin-left .24s ease; }
.topbar {
  position: sticky;
  top: 0;
  z-index: 30;
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 68px;
  padding: 0 28px;
  border-bottom: 1px solid rgba(203,211,214,.75);
  background: rgba(255,255,255,.88);
  backdrop-filter: blur(16px);
}
.breadcrumb { display: flex; align-items: center; gap: 10px; color: var(--ink-500); font-size: 12px; }
.breadcrumb i { color: var(--silver-300); font-style: normal; }
.breadcrumb strong { color: var(--ink-900); }
.top-actions { display: flex; align-items: center; gap: 16px; }
.environment { display: flex; align-items: center; gap: 7px; color: var(--ink-500); font-size: 10px; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; }
.environment i { width: 7px; height: 7px; border-radius: 50%; background: var(--success); }
.account-button { display: flex; align-items: center; gap: 10px; padding: 5px 8px 5px 5px; border: 1px solid transparent; border-radius: 12px; background: transparent; cursor: pointer; }
.account-button:hover { border-color: var(--silver-200); background: #fff; }
.account-copy { display: grid; min-width: 100px; text-align: left; }
.account-copy strong { font-size: 12px; }
.account-copy small { margin-top: 2px; color: var(--ink-500); font-size: 10px; }
.content { width: min(100% - 48px, 1560px); margin: 0 auto; padding: 32px 0 50px; }
.mobile-menu { display: none; }
.mobile-mask { display: none; }
.admin-shell.collapsed .sidebar { width: 76px; }
.admin-shell.collapsed .main-shell { margin-left: 76px; }
.admin-shell.collapsed .brand-copy,
.admin-shell.collapsed .workspace-chip,
.admin-shell.collapsed .nav-copy,
.admin-shell.collapsed .site-link span,
.admin-shell.collapsed .collapse-button span { display: none; }
.admin-shell.collapsed .brand { justify-content: center; padding-inline: 0; }
.admin-shell.collapsed .nav-item,
.admin-shell.collapsed .site-link,
.admin-shell.collapsed .collapse-button { justify-content: center; padding-inline: 0; }
@media (max-width: 900px) {
  .sidebar { transform: translateX(-100%); }
  .sidebar.mobile-open { transform: translateX(0); }
  .main-shell,.admin-shell.collapsed .main-shell { margin-left: 0; }
  .mobile-menu { display: grid; width: 38px; height: 38px; place-items: center; border: 1px solid var(--silver-200); border-radius: 10px; background: #fff; cursor: pointer; }
  .mobile-mask { position: fixed; inset: 0; z-index: 35; display: block; background: rgba(10,22,27,.46); backdrop-filter: blur(2px); }
  .breadcrumb span,.breadcrumb i { display: none; }
}
@media (max-width: 620px) {
  .topbar { padding: 0 14px; }
  .environment,.account-copy { display: none; }
  .content { width: min(100% - 24px, 1560px); padding-top: 22px; }
}
</style>

