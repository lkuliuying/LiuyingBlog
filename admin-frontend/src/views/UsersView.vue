<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { Delete, Edit, Refresh, Search, UserFilled, View } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'

import { adminApi } from '@/api/admin'
import { useAdminAuthStore } from '@/stores/auth'
import type { AdminUser } from '@/types'
import { formatDate } from '@/utils/format'

const auth = useAdminAuthStore()
const loading = ref(false)
const saving = ref(false)
const rows = ref<AdminUser[]>([])
const total = ref(0)
const detailOpen = ref(false)
const editOpen = ref(false)
const detail = ref<AdminUser | null>(null)
const formRef = ref<FormInstance>()
const filters = reactive({ page: 1, page_size: 15, search: '', role: '', active: '' })
const form = reactive({ id: 0, username: '', email: '', is_active: true, is_staff: false })
const rules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  email: [{ type: 'email', message: '邮箱格式不正确', trigger: 'blur' }],
}

async function load() {
  loading.value = true
  try {
    const result = await adminApi.users(filters)
    rows.value = result.results
    total.value = result.count
  } finally {
    loading.value = false
  }
}

function search() {
  filters.page = 1
  load()
}

async function showDetail(user: AdminUser) {
  loading.value = true
  try {
    detail.value = await adminApi.user(user.id)
    detailOpen.value = true
  } finally {
    loading.value = false
  }
}

function openEdit(user: AdminUser) {
  Object.assign(form, {
    id: user.id,
    username: user.username,
    email: user.email,
    is_active: user.is_active,
    is_staff: user.is_staff,
  })
  editOpen.value = true
}

async function save() {
  await formRef.value?.validate()
  saving.value = true
  try {
    await adminApi.updateUser(form.id, {
      username: form.username,
      email: form.email,
      is_active: form.is_active,
      is_staff: form.is_staff,
    })
    ElMessage.success('用户资料已更新')
    editOpen.value = false
    await load()
  } finally {
    saving.value = false
  }
}

async function toggleActive(user: AdminUser) {
  const action = user.is_active ? '禁用' : '启用'
  await ElMessageBox.confirm(`确定${action}用户“${user.username}”吗？`, `${action}用户`, {
    confirmButtonText: `确认${action}`,
    cancelButtonText: '取消',
    type: user.is_active ? 'warning' : 'info',
  })
  try {
    await adminApi.updateUser(user.id, { is_active: !user.is_active })
    ElMessage.success(`用户已${action}`)
    await load()
  } catch {
    user.is_active = !user.is_active
  }
}

function canDelete(user: AdminUser) {
  if (user.id === auth.user?.id) return false
  return !user.is_staff || Boolean(auth.user?.is_superuser)
}

async function remove(user: AdminUser) {
  const relatedContent = `${user.blog_count} 篇博客和 ${user.comment_count} 条评论`
  await ElMessageBox.confirm(
    `确定删除用户“${user.username}”吗？该用户的 ${relatedContent} 也会被一并删除，此操作不可恢复。`,
    '删除用户',
    {
      confirmButtonText: '确认删除',
      cancelButtonText: '取消',
      type: 'warning',
    },
  )
  await adminApi.deleteUser(user.id)
  ElMessage.success('用户已删除')
  if (rows.value.length === 1 && filters.page > 1) filters.page -= 1
  await load()
}

onMounted(load)
</script>

<template>
  <div>
    <header class="page-head">
      <div>
        <span class="page-kicker">COMMUNITY DIRECTORY</span>
        <h1 class="page-title">用户管理</h1>
        <p class="page-subtitle">查看社区成员状态、内容贡献和后台权限。</p>
      </div>
      <div class="page-actions"><el-button :icon="Refresh" @click="load">刷新</el-button></div>
    </header>

    <section class="filter-bar">
      <el-input v-model="filters.search" class="grow" clearable placeholder="搜索用户名或邮箱" :prefix-icon="Search" @keyup.enter="search" />
      <el-select v-model="filters.role" clearable placeholder="全部身份" style="width: 150px" @change="search">
        <el-option label="管理员" value="staff" />
        <el-option label="普通用户" value="user" />
      </el-select>
      <el-select v-model="filters.active" clearable placeholder="全部状态" style="width: 150px" @change="search">
        <el-option label="正常" value="true" />
        <el-option label="已禁用" value="false" />
      </el-select>
      <el-button type="primary" :icon="Search" @click="search">查询</el-button>
      <el-button @click="Object.assign(filters, { search: '', role: '', active: '' }); search()">重置</el-button>
    </section>

    <section class="panel">
      <div class="panel-head"><div><h2 class="panel-title">社区成员</h2><span class="panel-note">共 {{ total }} 位用户</span></div></div>
      <el-table v-loading="loading" :data="rows" row-key="id">
        <el-table-column label="用户" min-width="220">
          <template #default="{ row }">
            <div class="person">
              <el-avatar :size="40" :src="row.avatar">{{ row.username.slice(0, 1) }}</el-avatar>
              <span class="person-meta"><strong class="person-name">{{ row.username }}</strong><small class="person-sub">{{ row.email || '未设置邮箱' }}</small></span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="身份" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.is_superuser" type="danger" effect="plain">超级管理员</el-tag>
            <el-tag v-else-if="row.is_staff" effect="plain">管理员</el-tag>
            <el-tag v-else type="info" effect="plain">普通用户</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="内容贡献" width="150">
          <template #default="{ row }"><span class="contribution">{{ row.blog_count }} 博客 · {{ row.comment_count }} 评论</span></template>
        </el-table-column>
        <el-table-column label="注册时间" width="170">
          <template #default="{ row }">{{ formatDate(row.date_joined) }}</template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-switch :model-value="row.is_active" :disabled="row.id === auth.user?.id" @change="toggleActive(row)" />
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="190" align="right">
          <template #default="{ row }">
            <el-button link :icon="View" @click="showDetail(row)">查看</el-button>
            <el-button link type="primary" :icon="Edit" @click="openEdit(row)">编辑</el-button>
            <el-button v-if="canDelete(row)" link type="danger" :icon="Delete" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="table-footer">
        <span class="selection-note">管理员权限仅可由超级管理员调整</span>
        <el-pagination v-model:current-page="filters.page" v-model:page-size="filters.page_size" background layout="total, sizes, prev, pager, next" :total="total" :page-sizes="[10, 15, 30, 50]" @change="load" />
      </div>
    </section>

    <el-drawer v-model="detailOpen" title="用户档案" size="min(520px, 94vw)">
      <div v-if="detail" class="user-profile">
        <el-avatar :size="72" :src="detail.avatar">{{ detail.username.slice(0, 1) }}</el-avatar>
        <h2>{{ detail.username }}</h2>
        <p>{{ detail.email || '未设置邮箱' }}</p>
        <div class="profile-tags">
          <el-tag :type="detail.is_active ? 'success' : 'danger'" effect="plain">{{ detail.is_active ? '账号正常' : '账号禁用' }}</el-tag>
          <el-tag v-if="detail.is_staff" effect="plain">{{ detail.is_superuser ? '超级管理员' : '管理员' }}</el-tag>
        </div>
        <div class="user-stats">
          <div><strong>{{ detail.blog_count }}</strong><span>博客</span></div>
          <div><strong>{{ detail.comment_count }}</strong><span>评论</span></div>
          <div><strong>{{ detail.follower_count }}</strong><span>粉丝</span></div>
          <div><strong>{{ detail.following_count }}</strong><span>关注</span></div>
        </div>
        <dl>
          <div><dt>注册时间</dt><dd>{{ formatDate(detail.date_joined) }}</dd></div>
          <div><dt>最近登录</dt><dd>{{ formatDate(detail.last_login) }}</dd></div>
          <div><dt>用户 ID</dt><dd>#{{ detail.id }}</dd></div>
        </dl>
        <el-button type="primary" :icon="Edit" @click="detailOpen = false; openEdit(detail)">编辑用户资料</el-button>
      </div>
    </el-drawer>

    <el-dialog v-model="editOpen" title="编辑用户" width="480px">
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-form-item label="用户名" prop="username"><el-input v-model="form.username" /></el-form-item>
        <el-form-item label="邮箱" prop="email"><el-input v-model="form.email" /></el-form-item>
        <div class="permission-row">
          <div><strong>账号状态</strong><span>禁用后用户将无法登录</span></div>
          <el-switch v-model="form.is_active" :disabled="form.id === auth.user?.id" />
        </div>
        <div class="permission-row">
          <div><strong>管理后台权限</strong><span>仅超级管理员可以调整</span></div>
          <el-switch v-model="form.is_staff" :disabled="!auth.user?.is_superuser || form.id === auth.user?.id" />
        </div>
      </el-form>
      <template #footer>
        <el-button @click="editOpen = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">保存修改</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.contribution { color: var(--ink-500); font-size: 11px; white-space: nowrap; }
.user-profile { display: grid; justify-items: center; padding: 12px 8px; text-align: center; }
.user-profile h2 { margin: 14px 0 4px; font-size: 22px; }
.user-profile > p { margin: 0; color: var(--ink-500); font-size: 12px; }
.profile-tags { display: flex; gap: 8px; margin-top: 14px; }
.user-stats { display: grid; width: 100%; grid-template-columns: repeat(4, 1fr); gap: 8px; margin: 28px 0 18px; }
.user-stats div { display: grid; gap: 5px; padding: 14px 6px; border-radius: 12px; background: var(--silver-50); }
.user-stats strong { font-size: 20px; }
.user-stats span { color: var(--ink-500); font-size: 10px; }
dl { display: grid; width: 100%; gap: 1px; margin: 0 0 24px; overflow: hidden; border: 1px solid var(--silver-200); border-radius: 12px; background: var(--silver-200); text-align: left; }
dl div { display: grid; grid-template-columns: 90px 1fr; padding: 12px; background: #fff; }
dt { color: var(--ink-500); font-size: 11px; }
dd { margin: 0; font-size: 12px; text-align: right; }
.permission-row { display: flex; align-items: center; justify-content: space-between; gap: 16px; margin-top: 12px; padding: 15px; border: 1px solid var(--silver-200); border-radius: 12px; }
.permission-row div { display: grid; gap: 4px; }
.permission-row strong { font-size: 12px; }
.permission-row span { color: var(--ink-500); font-size: 10px; }
</style>

