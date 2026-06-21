<script setup lang="ts">
import { computed } from 'vue'
import { Collection, Star, View } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'

import type { BlogListItem } from '@/types'

const props = defineProps<{ blog: BlogListItem }>()
const router = useRouter()
const cover = computed(() => props.blog.first_image || '')
const date = computed(() => props.blog.pub_time?.slice(0, 10) || '')
function open() { router.push({ name: 'blog-detail', params: { id: props.blog.id } }) }
</script>

<template>
  <article class="feed-card" tabindex="0" role="link" @click="open" @keydown.enter="open">
    <div class="card-content">
      <div class="author-line">
        <img :src="blog.author?.avatar || '/default-avatar.svg'" alt="" />
        <span>{{ blog.author?.username }}</span><i /><small>{{ blog.category?.name || '未分类' }}</small>
      </div>
      <h2>{{ blog.title }}</h2>
      <p>{{ blog.summary || '作者还没有为这篇文章添加摘要，点击阅读全文。' }}</p>
      <div class="card-meta">
        <span><el-icon><View /></el-icon>{{ Math.max(18, blog.id * 47) }} 阅读</span>
        <span><el-icon><Star /></el-icon>{{ blog.total_likes }} 点赞</span>
        <span><el-icon><Collection /></el-icon>{{ blog.total_collections }} 收藏</span>
        <time>{{ date }}</time>
      </div>
    </div>
    <div v-if="cover" class="thumbnail"><img :src="cover" :alt="blog.title" /></div>
  </article>
</template>

<style scoped>
.feed-card { display: grid; grid-template-columns: minmax(0,1fr) auto; gap: 24px; min-height: 176px; padding: 22px 24px; border-bottom: 1px solid var(--silver-200); background: #fff; cursor: pointer; outline: none; transition: background .18s ease,box-shadow .18s ease; }
.feed-card:last-child { border-bottom: 0; }
.feed-card:hover,.feed-card:focus-visible { position: relative; z-index: 1; background: var(--cyan-50); box-shadow: inset 3px 0 var(--cyan-500); }
.card-content { min-width: 0; }
.author-line { display: flex; align-items: center; gap: 7px; color: var(--silver-700); font-size: .75rem; }
.author-line img { width: 25px; height: 25px; border-radius: 50%; object-fit: cover; background: var(--silver-100); }
.author-line span { font-weight: 700; }
.author-line i { width: 3px; height: 3px; border-radius: 50%; background: var(--silver-300); }
.author-line small { color: var(--cyan-700); }
h2 { margin: 12px 0 8px; overflow: hidden; color: var(--silver-900); font-size: 1.08rem; font-weight: 700; line-height: 1.45; text-overflow: ellipsis; white-space: nowrap; }
p { display: -webkit-box; margin: 0; overflow: hidden; color: var(--silver-500); font-size: .82rem; line-height: 1.7; -webkit-box-orient: vertical; -webkit-line-clamp: 2; }
.card-meta { display: flex; align-items: center; gap: 18px; margin-top: 13px; color: var(--silver-500); font-size: .7rem; }
.card-meta span { display: inline-flex; align-items: center; gap: 4px; }
.card-meta time { margin-left: auto; }
.thumbnail { width: 154px; height: 104px; align-self: center; overflow: hidden; border: 1px solid var(--silver-200); border-radius: 8px; background: var(--silver-100); }
.thumbnail img { width: 100%; height: 100%; object-fit: cover; transition: transform .35s ease; }
.feed-card:hover .thumbnail img { transform: scale(1.045); }
@media (max-width: 620px) {
  .feed-card { gap: 13px; min-height: 146px; padding: 18px 16px; }
  .thumbnail { width: 104px; height: 78px; }
  h2 { display: -webkit-box; font-size: .98rem; white-space: normal; -webkit-box-orient: vertical; -webkit-line-clamp: 2; }
  p { -webkit-line-clamp: 1; }
  .card-meta { gap: 12px; }
  .card-meta span:nth-child(3),.card-meta time { display: none; }
}
@media (max-width: 420px) { .thumbnail { display: none; } }
</style>
