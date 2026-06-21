import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'
import './styles/base.css'

async function start() {
  const app = createApp(App)
  const pinia = createPinia()

  app.use(pinia)

  // 路由开始首次导航前，先完整恢复 token 与用户资料。
  // 否则刷新后立即进入受保护页面时，会把已登录用户误判成游客。
  await useAuthStore().bootstrap()

  app.use(router)
  app.use(ElementPlus)
  app.mount('#app')
}

void start()
