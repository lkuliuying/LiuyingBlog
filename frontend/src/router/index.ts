import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { ElMessage } from 'element-plus'

import { useAuthStore } from '@/stores/auth'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('@/layouts/DefaultLayout.vue'),
    children: [
      { path: '', name: 'home', component: () => import('@/views/HomeView.vue') },
      { path: 'blog/:id', name: 'blog-detail', component: () => import('@/views/BlogDetailView.vue'), props: true },
      { path: 'pub', name: 'pub-blog', meta: { requiresAuth: true }, component: () => import('@/views/PubBlogView.vue') },
      { path: 'search', name: 'search', component: () => import('@/views/SearchView.vue') },
      { path: 'login', name: 'login', component: () => import('@/views/LoginView.vue') },
      { path: 'register', name: 'register', component: () => import('@/views/RegisterView.vue') },
      {
        path: 'profile',
        component: () => import('@/views/profile/ProfileLayout.vue'),
        meta: { requiresAuth: true },
        children: [
          { path: '', name: 'profile', redirect: { name: 'profile-blogs' } },
          { path: 'blogs', name: 'profile-blogs', component: () => import('@/views/profile/MyBlogs.vue') },
          { path: 'comments', name: 'profile-comments', component: () => import('@/views/profile/MyComments.vue') },
          { path: 'likes', name: 'profile-likes', component: () => import('@/views/profile/MyLikes.vue') },
          { path: 'collections', name: 'profile-collections', component: () => import('@/views/profile/MyCollections.vue') },
          { path: 'settings', name: 'profile-settings', component: () => import('@/views/profile/Settings.vue') },
        ],
      },
    ],
  },
  { path: '/:pathMatch(.*)*', redirect: { name: 'home' } },
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach(async (to) => {
  if (!to.meta?.requiresAuth) return true
  const auth = useAuthStore()
  await auth.bootstrap()
  if (!auth.isLogin) {
    ElMessage.warning('请先登录')
    return { name: 'login', query: { next: to.fullPath } }
  }
  return true
})

export default router
