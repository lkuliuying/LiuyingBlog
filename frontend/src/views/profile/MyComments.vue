<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'

import { authApi } from '@/api/auth'

interface RawComment {
  id: number
  blog: number
  content: string
  pub_time: string
}

const list = ref<RawComment[]>([])
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    const data = await authApi.myComments()
    list.value = data.results ?? data
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <section v-loading="loading">
    <h3>我的评论记录</h3>
    <ul v-if="list.length" class="list">
      <li v-for="c in list" :key="c.id">
        <div class="meta">
          评论于：<RouterLink :to="{ name: 'blog-detail', params: { id: c.blog } }">博客 #{{ c.blog }}</RouterLink>
        </div>
        <p>{{ c.content }}</p>
        <span class="time">{{ c.pub_time?.replace('T', ' ').slice(0, 16) }}</span>
      </li>
    </ul>
    <el-empty v-else description="还没有发表过评论" />
  </section>
</template>

<style scoped>
.list { list-style: none; padding: 0; }
.list li {
  border-left: 4px solid var(--primary-mint);
  padding: 12px 16px;
  background: #f8f9fa;
  border-radius: 0 8px 8px 0;
  margin-bottom: 12px;
}
.meta { font-size: 0.85rem; color: var(--font-color-sub); }
.meta a { color: var(--dark-mint); font-weight: 600; }
.time { font-size: 0.8rem; color: var(--font-color-sub); }
</style>
