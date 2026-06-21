<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'

import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const formRef = ref<FormInstance>()
const submitting = ref(false)

const form = reactive({ account: '', password: '' })

const rules: FormRules = {
  account: [{ required: true, message: '请输入邮箱或用户名', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于 6 位', trigger: 'blur' },
  ],
}

async function submit() {
  if (!formRef.value) return
  await formRef.value.validate()
  submitting.value = true
  try {
    await auth.login(form)
    ElMessage.success('登录成功')
    const next = (route.query.next as string) || '/'
    router.push(next)
  } catch {
    // 错误提示已在 axios 拦截器里给出
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="auth-card">
    <h2 class="section-title">登录</h2>
    <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
      <el-form-item label="邮箱 / 用户名" prop="account">
        <el-input v-model="form.account" placeholder="请输入绑定的邮箱或用户名" />
      </el-form-item>
      <el-form-item label="密码" prop="password">
        <el-input v-model="form.password" type="password" show-password placeholder="请输入密码" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" class="full" :loading="submitting" @click="submit">
          立即登录
        </el-button>
      </el-form-item>
      <div class="hint">
        还没有账号？
        <RouterLink :to="{ name: 'register' }">立即注册</RouterLink>
      </div>
    </el-form>
  </div>
</template>

<style scoped>
.auth-card {
  max-width: 380px;
  margin: 32px auto;
  background: #fff;
  padding: 32px;
  border-radius: 12px;
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.06);
}
.full { width: 100%; }
.hint {
  text-align: center;
  font-size: 0.9rem;
  color: var(--font-color-sub);
}
.hint a { color: var(--primary-mint); }
</style>
