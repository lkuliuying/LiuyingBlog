<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { Lock, User } from '@element-plus/icons-vue'
import AuthShell from '@/components/AuthShell.vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()
const formRef = ref<FormInstance>()
const submitting = ref(false)
const form = reactive({ account: '', password: '' })
const rules: FormRules = {
  account: [{ required: true, message: '请输入邮箱或用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }, { min: 6, message: '密码长度不能少于 6 位', trigger: 'blur' }],
}
async function submit() {
  if (!formRef.value) return
  await formRef.value.validate()
  submitting.value = true
  try {
    await auth.login(form)
    ElMessage.success('登录成功')
    router.push((route.query.next as string) || '/')
  } catch {
    // 错误提示已在 axios 拦截器里给出
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <AuthShell eyebrow="WELCOME BACK" title="欢迎回来" description="登录后继续阅读、创作与收藏你的技术灵感。" step="01">
    <el-form ref="formRef" class="auth-form" :model="form" :rules="rules" label-position="top" @submit.prevent="submit">
      <el-form-item label="邮箱 / 用户名" prop="account"><el-input v-model="form.account" :prefix-icon="User" placeholder="请输入绑定的邮箱或用户名" size="large" /></el-form-item>
      <el-form-item label="密码" prop="password"><el-input v-model="form.password" :prefix-icon="Lock" type="password" show-password placeholder="请输入密码" size="large" @keyup.enter="submit" /></el-form-item>
      <div class="form-meta"><span>使用已绑定的账户安全登录</span><span class="status">SECURE</span></div>
      <el-form-item class="submit-item"><el-button native-type="submit" type="primary" class="full" :loading="submitting">立即登录</el-button></el-form-item>
      <div class="hint">还没有账号？<RouterLink :to="{ name: 'register' }">立即注册</RouterLink></div>
    </el-form>
  </AuthShell>
</template>

<style scoped>
.auth-form :deep(.el-form-item){margin-bottom:22px}.auth-form :deep(.el-form-item__label){height:auto;padding-bottom:9px;color:var(--silver-700);font-size:.82rem;font-weight:700}
.auth-form :deep(.el-input__wrapper){min-height:50px;border:1px solid var(--silver-200);border-radius:11px;background:rgba(255,255,255,.78);box-shadow:none;transition:border-color .2s ease,box-shadow .2s ease,background .2s ease}
.auth-form :deep(.el-input__wrapper:hover){border-color:var(--silver-300)}.auth-form :deep(.el-input__wrapper.is-focus){border-color:var(--cyan-500);background:#fff;box-shadow:0 0 0 4px rgba(18,173,186,.11)}.auth-form :deep(.el-input__prefix){color:var(--cyan-700)}
.form-meta{display:flex;justify-content:space-between;margin:-6px 0 24px;color:var(--silver-500);font-size:.72rem}.status{color:var(--cyan-700);font-weight:800;letter-spacing:.12em}.submit-item{margin-bottom:18px!important}
.full{width:100%;height:50px;border:0;border-radius:11px;background:linear-gradient(110deg,var(--cyan-700),var(--cyan-500));font-weight:800;letter-spacing:.08em;box-shadow:0 12px 28px rgba(7,150,165,.22)}.full:hover,.full:focus{background:linear-gradient(110deg,#066f7a,#0ba9b7);transform:translateY(-1px)}
.hint{text-align:center;font-size:.84rem;color:var(--font-color-sub)}.hint a{margin-left:4px;color:var(--cyan-700);font-weight:800}
</style>
