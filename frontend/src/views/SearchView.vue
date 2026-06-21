<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import { blogApi } from '@/api/blog'
import BlogCard from '@/components/BlogCard.vue'
import type { BlogListItem, Paginated } from '@/types'

const route = useRoute()
const keyword = ref(String(route.query.q ?? ''))
const list = ref<BlogListItem[]>([])
const total = ref(0)
const loading = ref(false)

async function search() {
  loading.value = true
  try {
    const data: Paginated<BlogListItem> = await blogApi.list({ search: keyword.value })
    list.value = data.results
    total.value = data.count
  } finally {
    loading.value = false
  }
}

watch(() => route.query.q, (v) => {
  keyword.value = String(v ?? '')
  search()
})

onMounted(search)
</script>

<template>
  <section v-loading="loading">
    <h2 class="section-title">搜索结果：{{ keyword || '空' }}</h2>
    <p class="hint">共 {{ total }} 条结果</p>

    <div v-if="list.length" class="grid">
      <BlogCard v-for="b in list" :key="b.id" :blog="b" />
    </div>
    <el-empty v-else description="没有匹配的博客" />
  </section>
</template>

<style scoped>
.hint { color: var(--font-color-sub); margin: -16px 0 24px; }
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
}
</style>
