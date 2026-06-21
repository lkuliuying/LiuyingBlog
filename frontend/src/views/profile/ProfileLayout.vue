<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterView, useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

import { authApi } from '@/api/auth'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()
const uploading = ref(false)

const tabs = [
  { name: 'profile-blogs', label: '我发布的', icon: '📝' },
  { name: 'profile-comments', label: '我的评论', icon: '💬' },
  { name: 'profile-likes', label: '我的点赞', icon: '💖' },
  { name: 'profile-collections', label: '我的收藏', icon: '⭐' },
  { name: 'profile-settings', label: '账号设置', icon: '⚙️' },
]

const activeName = computed(() => String(route.name))
const userAvatar = computed(() => auth.user?.avatar || '/default-avatar.svg')

async function refreshStats() {
  await auth.fetchMe()
}

async function onAvatarChange(file: File | undefined) {
  if (!file) return
  if (file.size > 2 * 1024 * 1024) {
    ElMessage.warning('头像图片不能超过 2MB')
    return
  }
  uploading.value = true
  try {
    const data = await authApi.uploadAvatar(file)
    auth.patchUser({ avatar: data.avatar })
    ElMessage.success('头像修改成功')
  } finally {
    uploading.value = false
  }
}

function avatarPick(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  onAvatarChange(file)
  input.value = ''
}

onMounted(refreshStats)
</script>

<template>
  <div class="profile-layout">
    <aside class="sidebar">
      <div class="profile-card">
        <label class="avatar-wrap" :title="uploading ? '上传中...' : '点击修改头像'">
          <img :src="userAvatar" />
          <span class="camera">📷</span>
          <input type="file" accept="image/*" hidden @change="avatarPick" />
        </label>
        <div class="username">{{ auth.user?.username }}</div>
        <div class="email">{{ auth.user?.email || '未设置邮箱' }}</div>
        <div class="stats">
          <div><strong>{{ auth.stats?.blogs ?? 0 }}</strong><span>博客</span></div>
          <div><strong>{{ auth.stats?.comments ?? 0 }}</strong><span>评论</span></div>
        </div>
      </div>

      <ul class="menu">
        <li
          v-for="t in tabs"
          :key="t.name"
          :class="{ active: activeName === t.name }"
          @click="router.push({ name: t.name })"
        >
          <span>{{ t.icon }}</span>
          {{ t.label }}
        </li>
      </ul>
    </aside>

    <section class="content">
      <RouterView @stats-changed="refreshStats" />
    </section>
  </div>
</template>

<style scoped>
.profile-layout {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 24px;
}
.profile-card {
  background: #fff;
  padding: 24px;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.06);
}
.avatar-wrap {
  display: inline-block;
  position: relative;
  cursor: pointer;
  margin-bottom: 12px;
}
.avatar-wrap img {
  width: 96px;
  height: 96px;
  border-radius: 50%;
  object-fit: cover;
  background: var(--soft-grey);
}
.camera {
  position: absolute;
  right: -2px;
  bottom: 4px;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--primary-mint);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
}
.username {
  font-weight: 700;
  font-size: 1.1rem;
}
.email {
  color: var(--font-color-sub);
  font-size: 0.85rem;
  margin-top: 4px;
}
.stats {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin-top: 16px;
}
.stats div {
  display: flex;
  flex-direction: column;
  align-items: center;
  font-size: 0.85rem;
  color: var(--font-color-sub);
}
.stats strong {
  font-size: 1rem;
  color: #1f2933;
}
.menu {
  list-style: none;
  padding: 0;
  margin-top: 16px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.06);
  overflow: hidden;
}
.menu li {
  padding: 14px 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.95rem;
  border-left: 3px solid transparent;
}
.menu li:hover {
  background: #f8f9fa;
}
.menu li.active {
  background: rgba(0, 194, 146, 0.08);
  border-left-color: var(--primary-mint);
  color: var(--dark-mint);
  font-weight: 600;
}
.content {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.06);
  min-height: 480px;
}
</style>
