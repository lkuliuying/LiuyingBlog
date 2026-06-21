<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'

import { authApi } from '@/api/auth'

const router = useRouter()

const formRef = ref<FormInstance>()
const submitting = ref(false)
const captchaSending = ref(false)
const cooldown = ref(0)

const form = reactive({
  username: '',
  email: '',
  captcha: '',
  password: '',
})

const rules: FormRules = {
  username: [
    { required: true, message: '用户名不能为空', trigger: 'blur' },
    { min: 2, max: 20, message: '用户名长度 2-20 位', trigger: 'blur' },
  ],
  email: [
    { required: true, message: '邮箱不能为空', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' },
  ],
  captcha: [
    { required: true, message: '验证码不能为空', trigger: 'blur' },
    { len: 4, message: '验证码必须是 4 位', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '密码不能为空', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度 6-20 位', trigger: 'blur' },
  ],
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
  <div class="auth-card">
    <h2 class="section-title">注册</h2>
    <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
      <el-form-item label="用户名" prop="username">
        <el-input v-model="form.username" placeholder="请输入用户名" />
      </el-form-item>
      <el-form-item label="邮箱" prop="email">
        <el-input v-model="form.email" placeholder="请输入邮箱" />
      </el-form-item>
      <el-form-item label="验证码" prop="captcha">
        <div class="captcha-row">
          <el-input v-model="form.captcha" placeholder="请输入 4 位验证码" />
          <el-button
            :loading="captchaSending"
            :disabled="!form.email || cooldown > 0"
            @click="sendCaptcha"
          >
            {{ cooldown > 0 ? `${cooldown}s` : '获取验证码' }}
          </el-button>
        </div>
      </el-form-item>
      <el-form-item label="密码" prop="password">
        <el-input v-model="form.password" type="password" show-password placeholder="请输入密码" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" class="full" :loading="submitting" @click="submit">
          立即注册
        </el-button>
      </el-form-item>
      <div class="hint">
        已有账号？
        <RouterLink :to="{ name: 'login' }">直接登录</RouterLink>
      </div>
    </el-form>
  </div>
</template>

<style scoped>
.auth-card {
  max-width: 420px;
  margin: 32px auto;
  background: #fff;
  padding: 32px;
  border-radius: 12px;
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.06);
}
.captcha-row {
  display: flex;
  gap: 8px;
  width: 100%;
}
.full { width: 100%; }
.hint { text-align: center; font-size: 0.9rem; color: var(--font-color-sub); }
.hint a { color: var(--primary-mint); }
</style>
