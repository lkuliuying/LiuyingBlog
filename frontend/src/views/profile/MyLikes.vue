<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'

import { authApi } from '@/api/auth'
import type { BlogListItem, Paginated } from '@/types'

const list = ref<BlogListItem[]>([])
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    const data: Paginated<BlogListItem> = await authApi.myLikes()
    list.value = data.results
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <section v-loading="loading">
    <h3>点赞过的博客</h3>
    <ul v-if="list.length" class="list">
      <li v-for="b in list" :key="b.id">
        <RouterLink :to="{ name: 'blog-detail', params: { id: b.id } }">{{ b.title }}</RouterLink>
        <span class="badge">💖 {{ b.total_likes }}</span>
      </li>
    </ul>
    <el-empty v-else description="暂无点赞过的博客" />
  </section>
</template>

<style scoped>
.list { list-style: none; padding: 0; }
.list li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border: 1px solid var(--soft-grey);
  border-radius: 8px;
  margin-bottom: 8px;
}
.badge {
  background: rgba(255, 99, 132, 0.12);
  color: #d63384;
  border-radius: 999px;
  padding: 2px 10px;
  font-size: 0.8rem;
}
</style>
