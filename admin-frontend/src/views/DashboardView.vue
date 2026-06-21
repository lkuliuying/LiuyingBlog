<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ChatDotRound, Document, FolderOpened, Refresh, User } from '@element-plus/icons-vue'

import { adminApi } from '@/api/admin'
import type { DashboardData } from '@/types'
import { compactNumber, formatDate } from '@/utils/format'

const router = useRouter()
const loading = ref(false)
const data = ref<DashboardData | null>(null)

const metrics = computed(() => [
  { label: '社区用户', value: data.value?.totals.users || 0, today: data.value?.today.users || 0, icon: User, tone: 'cyan' },
  { label: '博客内容', value: data.value?.totals.blogs || 0, today: data.value?.today.blogs || 0, icon: Document, tone: 'blue' },
  { label: '社区评论', value: data.value?.totals.comments || 0, today: data.value?.today.comments || 0, icon: ChatDotRound, tone: 'green' },
  { label: '内容分类', value: data.value?.totals.categories || 0, today: null, icon: FolderOpened, tone: 'amber' },
])
const trendMax = computed(() => Math.max(1, ...(data.value?.trend.flatMap((item) => [item.users, item.blogs, item.comments]) || [1])))

async function load() {
  loading.value = true
  try {
    data.value = await adminApi.dashboard()
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <div v-loading="loading">
    <header class="page-head">
      <div>
        <span class="page-kicker">OPERATIONS OVERVIEW</span>
        <h1 class="page-title">社区工作台</h1>
        <p class="page-subtitle">快速掌握内容供给、社区互动和用户增长。</p>
      </div>
      <div class="page-actions">
        <el-button :icon="Refresh" @click="load">刷新数据</el-button>
        <el-button type="primary" :icon="Document" @click="router.push('/blogs')">管理博客</el-button>
      </div>
    </header>

    <section class="metric-grid">
      <article v-for="metric in metrics" :key="metric.label" class="metric-card" :class="metric.tone">
        <div class="metric-top">
          <span class="metric-icon"><el-icon><component :is="metric.icon" /></el-icon></span>
          <span v-if="metric.today !== null" class="today-badge">今日 +{{ metric.today }}</span>
        </div>
        <strong>{{ compactNumber(metric.value) }}</strong>
        <span>{{ metric.label }}</span>
        <i />
      </article>
    </section>

    <section class="dashboard-grid">
      <article class="panel trend-panel">
        <div class="panel-head">
          <div><h2 class="panel-title">近 7 日社区脉冲</h2><span class="panel-note">用户、博客与评论新增趋势</span></div>
          <div class="legend"><span class="users">用户</span><span class="blogs">博客</span><span class="comments">评论</span></div>
        </div>
        <div class="trend-list panel-body">
          <div v-for="day in data?.trend" :key="day.date" class="trend-row">
            <time>{{ day.date.slice(5) }}</time>
            <div class="bars">
              <span class="users" :style="{ width: `${Math.max(2, day.users / trendMax * 100)}%` }" :title="`用户 ${day.users}`" />
              <span class="blogs" :style="{ width: `${Math.max(2, day.blogs / trendMax * 100)}%` }" :title="`博客 ${day.blogs}`" />
              <span class="comments" :style="{ width: `${Math.max(2, day.comments / trendMax * 100)}%` }" :title="`评论 ${day.comments}`" />
            </div>
            <strong>{{ day.users + day.blogs + day.comments }}</strong>
          </div>
        </div>
      </article>

      <article class="panel focus-panel">
        <div class="panel-head"><div><h2 class="panel-title">今日焦点</h2><span class="panel-note">当前社区新增</span></div></div>
        <div class="focus-list">
          <div><span>新用户</span><strong>{{ data?.today.users || 0 }}</strong></div>
          <div><span>新博客</span><strong>{{ data?.today.blogs || 0 }}</strong></div>
          <div><span>新评论</span><strong>{{ data?.today.comments || 0 }}</strong></div>
        </div>
        <div class="focus-quote">“让知识保持流动，让灵感持续发光。”</div>
      </article>
    </section>

    <section class="recent-grid">
      <article class="panel">
        <div class="panel-head">
          <div><h2 class="panel-title">最近发布</h2><span class="panel-note">最新进入社区的内容</span></div>
          <el-button text type="primary" @click="router.push('/blogs')">查看全部</el-button>
        </div>
        <div class="recent-list">
          <button v-for="blog in data?.recent_blogs" :key="blog.id" type="button" class="recent-item" @click="router.push('/blogs')">
            <span class="content-index">{{ String(blog.id).padStart(2, '0') }}</span>
            <span class="recent-copy"><strong>{{ blog.title }}</strong><small>{{ blog.author.username }} · {{ blog.category?.name || '未分类' }}</small></span>
            <time>{{ formatDate(blog.pub_time, false) }}</time>
          </button>
          <div v-if="!data?.recent_blogs.length" class="empty-block">暂无博客内容</div>
        </div>
      </article>

      <article class="panel">
        <div class="panel-head">
          <div><h2 class="panel-title">最新评论</h2><span class="panel-note">需要关注的社区声音</span></div>
          <el-button text type="primary" @click="router.push('/comments')">前往治理</el-button>
        </div>
        <div class="recent-list">
          <button v-for="comment in data?.recent_comments" :key="comment.id" type="button" class="recent-item comment" @click="router.push('/comments')">
            <el-avatar :size="34" :src="comment.author.avatar">{{ comment.author.username.slice(0, 1) }}</el-avatar>
            <span class="recent-copy"><strong>{{ comment.content }}</strong><small>{{ comment.author.username }} · 《{{ comment.blog_title }}》</small></span>
            <time>{{ formatDate(comment.pub_time, false) }}</time>
          </button>
          <div v-if="!data?.recent_comments.length" class="empty-block">暂无社区评论</div>
        </div>
      </article>
    </section>
  </div>
</template>

<style scoped>
.metric-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 18px; }
.metric-card { position: relative; display: grid; min-height: 164px; padding: 20px; overflow: hidden; border: 1px solid var(--silver-200); border-radius: 16px; background: #fff; box-shadow: 0 8px 26px rgba(36,50,56,.04); }
.metric-card > i { position: absolute; right: -28px; bottom: -38px; width: 116px; height: 116px; border: 20px solid currentColor; border-radius: 50%; opacity: .035; }
.metric-top { display: flex; align-items: center; justify-content: space-between; }
.metric-icon { display: grid; width: 40px; height: 40px; place-items: center; border-radius: 12px; background: var(--cyan-50); color: var(--cyan-700); font-size: 18px; }
.today-badge { padding: 4px 7px; border-radius: 999px; background: var(--silver-50); color: var(--success); font-size: 10px; font-weight: 800; }
.metric-card > strong { align-self: end; margin-top: 16px; font-size: 34px; letter-spacing: -.05em; }
.metric-card > span:last-of-type { color: var(--ink-500); font-size: 12px; }
.metric-card.blue .metric-icon { background: #eef5fc; color: #4b83b4; }
.metric-card.green .metric-icon { background: #eef8f3; color: var(--success); }
.metric-card.amber .metric-icon { background: #fff6e9; color: var(--warning); }
.dashboard-grid { display: grid; grid-template-columns: minmax(0, 1.65fr) minmax(280px, .7fr); gap: 18px; margin-bottom: 18px; }
.legend { display: flex; gap: 14px; color: var(--ink-500); font-size: 10px; }
.legend span::before { display: inline-block; width: 7px; height: 7px; margin-right: 5px; border-radius: 2px; content: ''; background: currentColor; }
.legend .users { color: var(--cyan-600); }
.legend .blogs { color: #5f8fc0; }
.legend .comments { color: #5aaa7d; }
.trend-list { display: grid; gap: 13px; }
.trend-row { display: grid; grid-template-columns: 42px 1fr 28px; align-items: center; gap: 12px; }
.trend-row time { color: var(--ink-500); font-size: 10px; font-weight: 700; }
.trend-row > strong { color: var(--ink-700); font-size: 11px; text-align: right; }
.bars { display: grid; gap: 3px; }
.bars span { display: block; height: 4px; min-width: 3px; border-radius: 4px; transition: width .4s ease; }
.bars .users { background: var(--cyan-600); }
.bars .blogs { background: #78a5d0; }
.bars .comments { background: #79bd96; }
.focus-panel { display: flex; flex-direction: column; }
.focus-list { display: grid; grid-template-columns: repeat(3, 1fr); padding: 20px; gap: 8px; }
.focus-list div { display: grid; gap: 8px; padding: 12px 8px; border-radius: 12px; background: var(--silver-50); text-align: center; }
.focus-list span { color: var(--ink-500); font-size: 10px; }
.focus-list strong { font-size: 24px; }
.focus-quote { margin: auto 20px 20px; padding: 16px; border-left: 3px solid var(--cyan-500); background: var(--cyan-50); color: var(--cyan-800); font-size: 12px; line-height: 1.7; }
.recent-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }
.recent-list { padding: 4px 12px 12px; }
.recent-item { display: grid; width: 100%; grid-template-columns: 38px minmax(0,1fr) auto; align-items: center; gap: 11px; padding: 12px 8px; border: 0; border-bottom: 1px solid var(--silver-100); background: transparent; cursor: pointer; text-align: left; }
.recent-item:last-child { border-bottom: 0; }
.recent-item:hover { background: var(--cyan-50); }
.content-index { color: var(--silver-300); font-size: 11px; font-weight: 900; letter-spacing: .06em; }
.recent-copy { display: grid; min-width: 0; }
.recent-copy strong { overflow: hidden; font-size: 12px; text-overflow: ellipsis; white-space: nowrap; }
.recent-copy small { margin-top: 4px; overflow: hidden; color: var(--ink-500); font-size: 10px; text-overflow: ellipsis; white-space: nowrap; }
.recent-item time { color: var(--ink-500); font-size: 9px; }
.empty-block { min-height: 180px; }
@media (max-width: 1100px) {
  .metric-grid { grid-template-columns: repeat(2, 1fr); }
  .dashboard-grid,.recent-grid { grid-template-columns: 1fr; }
}
@media (max-width: 560px) {
  .metric-grid { grid-template-columns: 1fr; }
  .metric-card { min-height: 140px; }
  .legend { display: none; }
}
</style>

