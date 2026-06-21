<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Key, Lock, Right, User } from '@element-plus/icons-vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'

import { useAdminAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAdminAuthStore()
const formRef = ref<FormInstance>()
const loading = ref(false)
const form = reactive({ account: '', password: '' })
const rules: FormRules = {
  account: [{ required: true, message: '请输入管理员账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function submit() {
  await formRef.value?.validate()
  loading.value = true
  try {
    await auth.login(form)
    ElMessage.success('欢迎回到流萤管理台')
    const next = typeof route.query.next === 'string' ? route.query.next : '/'
    router.replace(next)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="login-page">
    <section class="brand-stage">
      <div class="stage-grid" />
      <div class="stage-content">
        <div class="stage-brand"><span>LY</span>流萤社区</div>
        <p class="eyebrow">COMMUNITY OPERATIONS</p>
        <h1>让每一束知识的微光，<br />都被认真照看。</h1>
        <p class="stage-copy">内容、用户与社区秩序，在一个清晰、克制而可靠的工作空间里流动。</p>
        <div class="stage-facts">
          <div><strong>01</strong><span>内容治理</span></div>
          <div><strong>02</strong><span>社区运营</span></div>
          <div><strong>03</strong><span>权限守卫</span></div>
        </div>
      </div>
      <div class="light-orbit"><i /><i /><i /></div>
    </section>

    <section class="login-stage">
      <div class="login-card">
        <div class="login-mark"><el-icon><Key /></el-icon></div>
        <p class="eyebrow">SECURE CONSOLE</p>
        <h2>登录管理后台</h2>
        <p class="login-copy">仅开放给已授权的流萤社区管理员。</p>
        <el-form ref="formRef" :model="form" :rules="rules" label-position="top" @submit.prevent="submit">
          <el-form-item label="管理员账号" prop="account">
            <el-input v-model="form.account" size="large" placeholder="用户名或邮箱" :prefix-icon="User" autocomplete="username" />
          </el-form-item>
          <el-form-item label="密码" prop="password">
            <el-input v-model="form.password" size="large" type="password" show-password placeholder="输入登录密码" :prefix-icon="Lock" autocomplete="current-password" @keyup.enter="submit" />
          </el-form-item>
          <el-button class="submit-button" type="primary" size="large" :loading="loading" native-type="submit">
            进入管理台<el-icon><Right /></el-icon>
          </el-button>
        </el-form>
        <div class="security-note"><i />登录行为受权限系统保护</div>
      </div>
      <a class="back-link" href="/">← 返回流萤社区</a>
    </section>
  </main>
</template>

<style scoped>
.login-page { display: grid; min-height: 100vh; grid-template-columns: minmax(420px, 1.15fr) minmax(420px, .85fr); background: var(--white); }
.brand-stage { position: relative; display: grid; min-height: 100vh; place-items: center; overflow: hidden; padding: 64px; background: #102127; color: #fff; }
.stage-grid { position: absolute; inset: 0; opacity: .18; background-image: linear-gradient(rgba(255,255,255,.08) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.08) 1px, transparent 1px); background-size: 48px 48px; mask-image: linear-gradient(to bottom right, #000, transparent 80%); }
.stage-content { position: relative; z-index: 2; width: min(100%, 650px); }
.stage-brand { display: flex; align-items: center; gap: 12px; margin-bottom: 88px; font-size: 15px; font-weight: 800; }
.stage-brand span { display: grid; width: 40px; height: 40px; place-items: center; border: 1px solid rgba(255,255,255,.2); border-radius: 12px; background: var(--cyan-600); font-size: 11px; letter-spacing: .08em; }
.eyebrow { margin: 0 0 16px; color: var(--cyan-500); font-size: 10px; font-weight: 900; letter-spacing: .22em; }
h1 { margin: 0; font-size: clamp(40px, 5vw, 72px); line-height: 1.14; letter-spacing: -.06em; }
.stage-copy { max-width: 560px; margin: 28px 0 44px; color: #9bb0b5; font-size: 16px; line-height: 1.9; }
.stage-facts { display: flex; gap: 36px; }
.stage-facts div { display: grid; gap: 5px; }
.stage-facts strong { color: var(--cyan-500); font-size: 11px; letter-spacing: .12em; }
.stage-facts span { color: #c8d6d9; font-size: 12px; }
.light-orbit { position: absolute; right: -180px; bottom: -180px; width: 520px; height: 520px; border: 1px solid rgba(18,173,186,.18); border-radius: 50%; }
.light-orbit::before,.light-orbit::after { position: absolute; content: ''; border: 1px solid rgba(18,173,186,.12); border-radius: 50%; }
.light-orbit::before { inset: 70px; }
.light-orbit::after { inset: 145px; }
.light-orbit i { position: absolute; width: 8px; height: 8px; border-radius: 50%; background: var(--cyan-500); box-shadow: 0 0 24px var(--cyan-500); }
.light-orbit i:nth-child(1) { top: 55px; left: 118px; }
.light-orbit i:nth-child(2) { top: 184px; left: 36px; }
.light-orbit i:nth-child(3) { top: 140px; right: 72px; }
.login-stage { position: relative; display: grid; min-height: 100vh; place-items: center; padding: 52px; background: radial-gradient(circle at 100% 0, var(--cyan-50), transparent 36%), #f9fbfb; }
.login-card { width: min(100%, 430px); padding: 42px; border: 1px solid var(--silver-200); border-radius: 22px; background: rgba(255,255,255,.9); box-shadow: 0 24px 70px rgba(28,49,56,.1); backdrop-filter: blur(16px); animation: card-in .6s cubic-bezier(.2,.8,.2,1) both; }
@keyframes card-in { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: translateY(0); } }
.login-mark { display: grid; width: 46px; height: 46px; margin-bottom: 24px; place-items: center; border-radius: 14px; background: var(--cyan-100); color: var(--cyan-700); font-size: 20px; }
h2 { margin: 0; font-size: 30px; letter-spacing: -.04em; }
.login-copy { margin: 10px 0 30px; color: var(--ink-500); font-size: 13px; }
.submit-button { width: 100%; margin-top: 8px; font-weight: 800; }
.submit-button .el-icon { margin-left: 8px; }
.security-note { display: flex; align-items: center; justify-content: center; gap: 8px; margin-top: 24px; color: var(--ink-500); font-size: 11px; }
.security-note i { width: 6px; height: 6px; border-radius: 50%; background: var(--success); }
.back-link { position: absolute; right: 32px; bottom: 28px; color: var(--ink-500); font-size: 12px; }
.back-link:hover { color: var(--cyan-700); }
:deep(.el-form-item__label) { color: var(--ink-700); font-size: 12px; font-weight: 800; }
@media (max-width: 900px) {
  .login-page { grid-template-columns: 1fr; }
  .brand-stage { display: none; }
  .login-stage { padding: 24px; }
  .login-card { padding: 30px 24px; }
}
</style>

