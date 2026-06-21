<script setup lang="ts">
import { reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'

import { authApi } from '@/api/auth'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

const profileFormRef = ref<FormInstance>()
const profile = reactive({
  username: auth.user?.username ?? '',
  email: auth.user?.email ?? '',
})

watch(
  () => auth.user,
  (u) => {
    if (u) {
      profile.username = u.username
      profile.email = u.email
    }
  },
  { immediate: true },
)

const profileRules: FormRules = {
  username: [{ required: true, message: '用户名不能为空', trigger: 'blur' }],
  email: [{ type: 'email', message: '邮箱格式不正确', trigger: 'blur' }],
}

const profileSubmitting = ref(false)
async function submitProfile() {
  if (!profileFormRef.value) return
  await profileFormRef.value.validate()
  profileSubmitting.value = true
  try {
    const u = await authApi.updateProfile(profile)
    auth.patchUser(u)
    ElMessage.success('基本信息修改成功')
  } finally {
    profileSubmitting.value = false
  }
}

const passwordFormRef = ref<FormInstance>()
const password = reactive({
  old_password: '',
  new_password1: '',
  new_password2: '',
})

const passwordRules: FormRules = {
  old_password: [{ required: true, message: '请输入旧密码', trigger: 'blur' }],
  new_password1: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于 6 位', trigger: 'blur' },
  ],
  new_password2: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (_rule, value, cb) => {
        if (value !== password.new_password1) {
          cb(new Error('两次输入的密码不一致'))
        } else {
          cb()
        }
      },
      trigger: 'blur',
    },
  ],
}

const passwordSubmitting = ref(false)
async function submitPassword() {
  if (!passwordFormRef.value) return
  await passwordFormRef.value.validate()
  passwordSubmitting.value = true
  try {
    await authApi.changePassword(password)
    ElMessage.success('密码修改成功')
    password.old_password = ''
    password.new_password1 = ''
    password.new_password2 = ''
  } finally {
    passwordSubmitting.value = false
  }
}
</script>

<template>
  <section>
    <h3>基本资料</h3>
    <el-form ref="profileFormRef" :model="profile" :rules="profileRules" label-position="top">
      <el-form-item label="用户名" prop="username">
        <el-input v-model="profile.username" />
      </el-form-item>
      <el-form-item label="电子邮箱" prop="email">
        <el-input v-model="profile.email" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" :loading="profileSubmitting" @click="submitProfile">
          保存修改
        </el-button>
      </el-form-item>
    </el-form>

    <el-divider />

    <h3>安全设置</h3>
    <el-form ref="passwordFormRef" :model="password" :rules="passwordRules" label-position="top">
      <el-form-item label="当前密码" prop="old_password">
        <el-input v-model="password.old_password" type="password" show-password />
      </el-form-item>
      <el-form-item label="新密码" prop="new_password1">
        <el-input v-model="password.new_password1" type="password" show-password />
      </el-form-item>
      <el-form-item label="确认新密码" prop="new_password2">
        <el-input v-model="password.new_password2" type="password" show-password />
      </el-form-item>
      <el-form-item>
        <el-button type="warning" :loading="passwordSubmitting" @click="submitPassword">
          重置密码
        </el-button>
      </el-form-item>
    </el-form>
  </section>
</template>
