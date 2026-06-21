<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  ChatLineSquare, Clock, Collection, Download, House, Reading,
  Star, User, View,
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

import { blogApi } from '@/api/blog'
import BlogCard from '@/components/BlogCard.vue'
import type { BlogCategory, BlogListItem, Paginated } from '@/types'

const router = useRouter()
const list = ref<BlogListItem[]>([])
const categories = ref<BlogCategory[]>([])
const total = ref(0)
const page = ref(1)
const loading = ref(false)
const activeCategory = ref<number | 'all'>('all')
const followed = ref<number[]>([])

const filteredList = computed(() => activeCategory.value === 'all'
  ? list.value
  : list.value.filter((item) => item.category?.id === activeCategory.value))
const authors = computed(() => {
  const seen = new Set<number>()
  return list.value.map((item) => item.author).filter((author) => {
    if (!author || seen.has(author.id)) return false
    seen.add(author.id)
    return true
  }).slice(0, 7)
})

const primaryNav = [
  { label: '首页', icon: House, action: () => router.push({ name: 'home' }) },
  { label: '博客', icon: Reading, active: true, action: () => window.scrollTo({ top: 0, behavior: 'smooth' }) },
  { label: '发布文章', icon: ChatLineSquare, action: () => router.push({ name: 'pub-blog' }) },
  { label: '发现作者', icon: User, action: () => document.querySelector('.right-panel')?.scrollIntoView({ behavior: 'smooth' }) },
]
const personalNav = [
  { label: '我的收藏', icon: Collection, action: () => router.push({ name: 'profile-collections' }) },
  { label: '点赞文章', icon: Star, action: () => router.push({ name: 'profile-likes' }) },
  { label: '浏览历史', icon: Clock, action: () => ElMessage.info('浏览历史功能正在准备中') },
  { label: '离线下载', icon: Download, action: () => ElMessage.info('暂不支持离线下载') },
]

async function load(p = 1) {
  loading.value = true
  try {
    const [blogs, categoryList] = await Promise.all([
      blogApi.list({ page: p }) as Promise<Paginated<BlogListItem>>,
      blogApi.categories(),
    ])
    list.value = blogs.results
    total.value = blogs.count
    categories.value = categoryList
    page.value = p
  } finally { loading.value = false }
}
function onPage(p: number) { load(p); window.scrollTo({ top: 0, behavior: 'smooth' }) }
function toggleFollow(id: number) {
  followed.value = followed.value.includes(id)
    ? followed.value.filter((item) => item !== id)
    : [...followed.value, id]
}
onMounted(() => load(1))
</script>

<template>
  <div class="community-layout">
    <aside class="left-sidebar">
      <nav class="side-nav">
        <button v-for="item in primaryNav" :key="item.label" type="button" :class="{ active: item.active }" @click="item.action">
          <el-icon><component :is="item.icon" /></el-icon><span>{{ item.label }}</span>
        </button>
      </nav>
      <div class="nav-divider" />
      <p class="nav-caption">个人空间</p>
      <nav class="side-nav secondary">
        <button v-for="item in personalNav" :key="item.label" type="button" @click="item.action">
          <el-icon><component :is="item.icon" /></el-icon><span>{{ item.label }}</span>
        </button>
      </nav>
      <div class="sidebar-card">
        <span class="sidebar-card-label">创作中心</span>
        <strong>分享你的新发现</strong>
        <p>记录实践、代码与思考，让知识被更多人看见。</p>
        <button type="button" @click="router.push({ name: 'pub-blog' })">开始创作</button>
      </div>
    </aside>

    <section class="feed-panel" v-loading="loading">
      <div class="feed-tabs">
        <button type="button" :class="{ active: activeCategory === 'all' }" @click="activeCategory = 'all'">推荐</button>
        <button v-for="category in categories" :key="category.id" type="button" :class="{ active: activeCategory === category.id }" @click="activeCategory = category.id">
          {{ category.name }}
        </button>
      </div>

      <div class="feed-heading">
        <div><h1>技术博客</h1><p>来自社区的最新实践、经验与灵感</p></div>
        <span><strong>{{ total }}</strong> 篇内容</span>
      </div>

      <div v-if="filteredList.length" class="article-list">
        <BlogCard v-for="blog in filteredList" :key="blog.id" :blog="blog" />
      </div>
      <div v-else-if="!loading" class="empty-feed">
        <el-icon><Reading /></el-icon><strong>这个分类还没有文章</strong><span>换个分类看看，或者发布第一篇。</span>
      </div>

      <div v-if="total > 10 && activeCategory === 'all'" class="pager">
        <el-pagination background layout="prev, pager, next" :total="total" :page-size="10" :current-page="page" @current-change="onPage" />
      </div>
    </section>

    <aside class="right-panel">
      <section class="side-section">
        <header><h2>作者推荐</h2><button type="button" @click="ElMessage.info('已为你刷新推荐')">换一批</button></header>
        <div class="author-list">
          <div v-for="author in authors" :key="author.id" class="author-row">
            <img :src="author.avatar || '/default-avatar.svg'" alt="" />
            <div><strong>{{ author.username }}</strong><span>持续分享技术与生活</span></div>
            <button type="button" :class="{ followed: followed.includes(author.id) }" @click="toggleFollow(author.id)">
              {{ followed.includes(author.id) ? '已关注' : '关注' }}
            </button>
          </div>
        </div>
      </section>

      <section class="side-section hot-section">
        <header><h2>热门话题</h2></header>
        <button v-for="(category, index) in categories.slice(0, 6)" :key="category.id" type="button" @click="activeCategory = category.id">
          <span>{{ String(index + 1).padStart(2, '0') }}</span><strong># {{ category.name }}</strong><small>{{ Math.max(3, total - index) }} 篇讨论</small>
        </button>
      </section>

      <section class="community-note">
        <el-icon><View /></el-icon><div><strong>流萤社区公约</strong><p>友善交流，尊重原创，共同维护高质量内容环境。</p></div>
      </section>
    </aside>
  </div>
</template>

<style scoped>
.community-layout { display: grid; grid-template-columns: 220px minmax(480px, 1fr) 310px; gap: 22px; width: min(100% - 40px, 1540px); margin: 0 auto; padding: 22px 0 40px; }
.left-sidebar,.right-panel { position: sticky; top: 86px; align-self: start; max-height: calc(100vh - 104px); overflow-y: auto; scrollbar-width: thin; }
.left-sidebar { padding: 8px; border: 1px solid var(--silver-200); border-radius: 12px; background: #fff; }
.side-nav { display: grid; gap: 4px; }
.side-nav button { display: flex; align-items: center; gap: 13px; width: 100%; padding: 12px 14px; border: 0; border-radius: 9px; background: transparent; cursor: pointer; text-align: left; font-size: .92rem; }
.side-nav button:hover { background: var(--silver-50); color: var(--cyan-700); }
.side-nav button.active { background: var(--cyan-50); color: var(--cyan-700); font-weight: 700; box-shadow: inset 3px 0 var(--cyan-600); }
.side-nav .el-icon { font-size: 1.12rem; }
.nav-divider { height: 1px; margin: 12px 8px; background: var(--silver-200); }
.nav-caption { margin: 10px 14px 7px; color: var(--silver-500); font-size: .72rem; font-weight: 700; letter-spacing: .08em; }
.sidebar-card { margin: 16px 4px 4px; padding: 17px; border: 1px solid #b9e4e7; border-radius: 10px; background: var(--cyan-50); }
.sidebar-card-label { color: var(--cyan-700); font-size: .7rem; font-weight: 800; }
.sidebar-card strong { display: block; margin-top: 8px; font-size: .98rem; }
.sidebar-card p { margin: 8px 0 14px; color: var(--silver-700); font-size: .76rem; line-height: 1.65; }
.sidebar-card button { width: 100%; padding: 9px; border: 0; border-radius: 7px; background: var(--cyan-600); color: #fff; cursor: pointer; font-weight: 700; }
.feed-panel { min-width: 0; border: 1px solid var(--silver-200); border-radius: 12px; background: #fff; }
.feed-tabs { display: flex; gap: 5px; padding: 14px 18px 0; overflow-x: auto; border-bottom: 1px solid var(--silver-200); scrollbar-width: none; }
.feed-tabs button { flex: 0 0 auto; padding: 10px 13px 12px; border: 0; border-bottom: 2px solid transparent; background: transparent; color: var(--silver-500); cursor: pointer; font-size: .84rem; }
.feed-tabs button:hover,.feed-tabs button.active { color: var(--cyan-700); }
.feed-tabs button.active { border-bottom-color: var(--cyan-600); font-weight: 700; }
.feed-heading { display: flex; align-items: end; justify-content: space-between; padding: 22px 24px 16px; }
.feed-heading h1 { margin: 0; font-size: 1.35rem; }
.feed-heading p { margin: 7px 0 0; color: var(--silver-500); font-size: .8rem; }
.feed-heading > span { color: var(--silver-500); font-size: .75rem; }
.feed-heading > span strong { color: var(--cyan-700); font-size: 1.1rem; }
.article-list { border-top: 1px solid var(--silver-100); }
.pager { display: flex; justify-content: center; padding: 26px; }
.empty-feed { display: grid; min-height: 320px; place-items: center; align-content: center; gap: 10px; color: var(--silver-500); }
.empty-feed .el-icon { color: var(--cyan-500); font-size: 2rem; }
.empty-feed strong { color: var(--silver-700); }
.right-panel { display: grid; gap: 16px; }
.side-section,.community-note { border: 1px solid var(--silver-200); border-radius: 12px; background: #fff; }
.side-section { padding: 18px; }
.side-section header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
.side-section h2 { margin: 0; font-size: 1rem; }
.side-section header button { border: 0; background: transparent; color: var(--cyan-700); cursor: pointer; font-size: .74rem; }
.author-list { display: grid; }
.author-row { display: grid; grid-template-columns: 40px 1fr auto; gap: 10px; align-items: center; padding: 11px 0; border-bottom: 1px solid var(--silver-100); }
.author-row:last-child { border-bottom: 0; }
.author-row img { width: 40px; height: 40px; border-radius: 50%; object-fit: cover; background: var(--silver-100); }
.author-row div { min-width: 0; }
.author-row strong,.author-row span { display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.author-row strong { font-size: .82rem; }
.author-row span { margin-top: 4px; color: var(--silver-500); font-size: .68rem; }
.author-row button { padding: 5px 10px; border: 1px solid var(--cyan-500); border-radius: 16px; background: #fff; color: var(--cyan-700); cursor: pointer; font-size: .7rem; }
.author-row button.followed { border-color: var(--silver-300); background: var(--silver-100); color: var(--silver-500); }
.hot-section > button { display: grid; grid-template-columns: 28px 1fr auto; align-items: center; gap: 8px; width: 100%; padding: 11px 0; border: 0; border-bottom: 1px solid var(--silver-100); background: transparent; cursor: pointer; text-align: left; }
.hot-section > button:last-child { border-bottom: 0; }
.hot-section > button > span { color: var(--cyan-500); font-family: Georgia,serif; font-size: .75rem; }
.hot-section > button strong { font-size: .78rem; }
.hot-section > button small { color: var(--silver-500); font-size: .65rem; }
.community-note { display: flex; gap: 12px; padding: 17px; color: var(--silver-700); }
.community-note > .el-icon { flex: 0 0 auto; color: var(--cyan-600); font-size: 1.2rem; }
.community-note strong { font-size: .8rem; }
.community-note p { margin: 6px 0 0; color: var(--silver-500); font-size: .7rem; line-height: 1.6; }
@media (max-width: 1180px) { .community-layout { grid-template-columns: 190px minmax(440px,1fr); } .right-panel { display: none; } }
@media (max-width: 860px) { .community-layout { grid-template-columns: 1fr; width: min(100% - 24px, 760px); padding-top: 12px; } .left-sidebar { display: none; } .feed-panel { border-radius: 10px; } }
@media (max-width: 560px) { .community-layout { width: 100%; padding: 0; } .feed-panel { border-right: 0; border-left: 0; border-radius: 0; } .feed-heading { padding: 18px 16px 12px; } .feed-heading p { display: none; } }
</style>
