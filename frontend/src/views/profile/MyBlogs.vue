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
    const data: Paginated<BlogListItem> = await authApi.myBlogs()
    list.value = data.results
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <section v-loading="loading">
    <h3>我发布的博客</h3>
    <ul v-if="list.length" class="list">
      <li v-for="b in list" :key="b.id">
        <RouterLink :to="{ name: 'blog-detail', params: { id: b.id } }">{{ b.title }}</RouterLink>
        <span class="date">{{ b.pub_time?.slice(0, 10) }}</span>
      </li>
    </ul>
    <el-empty v-else description="还没有发布过任何博客" />
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
.list li a { color: #1f2933; font-weight: 500; }
.date { color: var(--font-color-sub); font-size: 0.85rem; }
</style>
