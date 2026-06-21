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
    const data: Paginated<BlogListItem> = await authApi.myCollections()
    list.value = data.results
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <section v-loading="loading">
    <h3>收藏的文章</h3>
    <ul v-if="list.length" class="list">
      <li v-for="b in list" :key="b.id">
        <RouterLink :to="{ name: 'blog-detail', params: { id: b.id } }">⭐ {{ b.title }}</RouterLink>
        <span class="author">作者：{{ b.author?.username }}</span>
      </li>
    </ul>
    <el-empty v-else description="还没有收藏过文章" />
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
.author { color: var(--font-color-sub); font-size: 0.85rem; }
</style>
