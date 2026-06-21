import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'

import { useAdminAuthStore } from '@/stores/auth'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'admin-login',
    component: () => import('@/views/LoginView.vue'),
    meta: { guestOnly: true },
  },
  {
    path: '/',
    component: () => import('@/layouts/AdminLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '', name: 'dashboard', component: () => import('@/views/DashboardView.vue') },
      { path: 'blogs', name: 'blogs', component: () => import('@/views/BlogsView.vue') },
      { path: 'categories', name: 'categories', component: () => import('@/views/CategoriesView.vue') },
      { path: 'comments', name: 'comments', component: () => import('@/views/CommentsView.vue') },
      { path: 'users', name: 'users', component: () => import('@/views/UsersView.vue') },
    ],
  },
  { path: '/:pathMatch(.*)*', redirect: { name: 'dashboard' } },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

router.beforeEach(async (to) => {
  const auth = useAdminAuthStore()
  await auth.bootstrap()
  if (to.meta.requiresAuth && !auth.isLogin) {
    return { name: 'admin-login', query: { next: to.fullPath } }
  }
  if (to.meta.guestOnly && auth.isLogin) return { name: 'dashboard' }
  return true
})

export default router

