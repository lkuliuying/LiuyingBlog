<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { Key, Lock, Message, User } from '@element-plus/icons-vue'
import { authApi } from '@/api/auth'
import AuthShell from '@/components/AuthShell.vue'

const router = useRouter()
const formRef = ref<FormInstance>()
const submitting = ref(false)
const captchaSending = ref(false)
const cooldown = ref(0)
const form = reactive({ username: '', email: '', captcha: '', password: '' })
const rules: FormRules = {
  username: [{ required: true, message: '用户名不能为空', trigger: 'blur' }, { min: 2, max: 20, message: '用户名长度 2-20 位', trigger: 'blur' }],
  email: [{ required: true, message: '邮箱不能为空', trigger: 'blur' }, { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }],
  captcha: [{ required: true, message: '验证码不能为空', trigger: 'blur' }, { len: 6, message: '验证码必须是 6 位', trigger: 'blur' }],
  password: [{ required: true, message: '密码不能为空', trigger: 'blur' }, { min: 6, max: 20, message: '密码长度 6-20 位', trigger: 'blur' }],
}
async function sendCaptcha() {
  if (!form.email || cooldown.value > 0) return
  captchaSending.value = true
  try {
    await authApi.captcha(form.email)
    ElMessage.success('验证码已发送，请检查邮箱')
    cooldown.value = 60
    const timer = setInterval(() => {
      cooldown.value -= 1
      if (cooldown.value <= 0) clearInterval(timer)
    }, 1000)
  } finally {
    captchaSending.value = false
  }
}
async function submit() {
  if (!formRef.value) return
  await formRef.value.validate()
  submitting.value = true
  try {
    await authApi.register(form)
    ElMessage.success('注册成功，请登录')
    router.push({ name: 'login' })
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <AuthShell eyebrow="JOIN THE FLOW" title="创建你的账号" description="用一个新身份加入社区，开始记录并分享你的技术旅程。" step="02">
    <el-form ref="formRef" class="auth-form" :model="form" :rules="rules" label-position="top" @submit.prevent="submit">
      <div class="field-grid">
        <el-form-item label="用户名" prop="username"><el-input v-model="form.username" :prefix-icon="User" placeholder="2–20 位用户名" size="large" /></el-form-item>
        <el-form-item label="邮箱" prop="email"><el-input v-model="form.email" :prefix-icon="Message" placeholder="请输入常用邮箱" size="large" /></el-form-item>
      </div>
      <el-form-item label="邮箱验证码" prop="captcha">
        <div class="captcha-row">
          <el-input v-model="form.captcha" :prefix-icon="Key" placeholder="请输入 6 位验证码" size="large" />
          <el-button class="captcha-button" :loading="captchaSending" :disabled="!form.email || cooldown > 0" @click="sendCaptcha">{{ cooldown > 0 ? `${cooldown}s` : '获取验证码' }}</el-button>
        </div>
      </el-form-item>
      <el-form-item label="设置密码" prop="password"><el-input v-model="form.password" :prefix-icon="Lock" type="password" show-password placeholder="请输入 6–20 位密码" size="large" @keyup.enter="submit" /></el-form-item>
      <el-form-item class="submit-item"><el-button native-type="submit" type="primary" class="full" :loading="submitting">立即注册</el-button></el-form-item>
      <div class="hint">已有账号？<RouterLink :to="{ name: 'login' }">直接登录</RouterLink></div>
    </el-form>
  </AuthShell>
</template>

<style scoped>
.auth-form :deep(.el-form-item){margin-bottom:18px}.auth-form :deep(.el-form-item__label){height:auto;padding-bottom:8px;color:var(--silver-700);font-size:.8rem;font-weight:700}
.auth-form :deep(.el-input__wrapper){min-height:48px;border:1px solid var(--silver-200);border-radius:11px;background:rgba(255,255,255,.78);box-shadow:none;transition:border-color .2s ease,box-shadow .2s ease,background .2s ease}
.auth-form :deep(.el-input__wrapper:hover){border-color:var(--silver-300)}.auth-form :deep(.el-input__wrapper.is-focus){border-color:var(--cyan-500);background:#fff;box-shadow:0 0 0 4px rgba(18,173,186,.11)}.auth-form :deep(.el-input__prefix){color:var(--cyan-700)}
.field-grid{display:grid;grid-template-columns:1fr 1.18fr;gap:12px}.captcha-row{display:flex;gap:10px;width:100%}.captcha-button{height:48px;flex:0 0 112px;border-color:rgba(7,150,165,.26);border-radius:11px;background:var(--cyan-50);color:var(--cyan-700);font-weight:700}.captcha-button:not(.is-disabled):hover{border-color:var(--cyan-500);background:var(--cyan-100);color:var(--cyan-700)}
.submit-item{margin-top:4px;margin-bottom:16px!important}.full{width:100%;height:50px;border:0;border-radius:11px;background:linear-gradient(110deg,var(--cyan-700),var(--cyan-500));font-weight:800;letter-spacing:.08em;box-shadow:0 12px 28px rgba(7,150,165,.22)}.full:hover,.full:focus{background:linear-gradient(110deg,#066f7a,#0ba9b7);transform:translateY(-1px)}
.hint{text-align:center;color:var(--font-color-sub);font-size:.84rem}.hint a{margin-left:4px;color:var(--cyan-700);font-weight:800}
@media(max-width:1080px){.field-grid{grid-template-columns:1fr;gap:0}}@media(max-width:420px){.captcha-row{align-items:stretch}.captcha-button{flex-basis:102px;padding:0 10px}}
</style>
