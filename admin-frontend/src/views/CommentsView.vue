<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ChatDotRound, Delete, Refresh, Search, View } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

import { adminApi } from '@/api/admin'
import type { AdminComment } from '@/types'
import { formatDate } from '@/utils/format'

const loading = ref(false)
const rows = ref<AdminComment[]>([])
const selected = ref<AdminComment[]>([])
const total = ref(0)
const detailOpen = ref(false)
const detail = ref<AdminComment | null>(null)
const filters = reactive({ page: 1, page_size: 15, search: '' })

async function load() {
  loading.value = true
  try {
    const result = await adminApi.comments(filters)
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

async function remove(comment: AdminComment) {
  await ElMessageBox.confirm('确定删除这条评论吗？其回复也可能被一并删除。', '删除评论', {
    confirmButtonText: '确认删除',
    cancelButtonText: '取消',
    type: 'warning',
  })
  await adminApi.deleteComment(comment.id)
  ElMessage.success('评论已删除')
  await load()
}

async function bulkRemove() {
  if (!selected.value.length) return
  await ElMessageBox.confirm(`确定删除选中的 ${selected.value.length} 条评论吗？`, '批量删除', {
    confirmButtonText: '确认删除',
    cancelButtonText: '取消',
    type: 'warning',
  })
  await adminApi.bulkDeleteComments(selected.value.map((item) => item.id))
  ElMessage.success('已完成批量删除')
  await load()
}

function showDetail(comment: AdminComment) {
  detail.value = comment
  detailOpen.value = true
}

onMounted(load)
</script>

<template>
  <div>
    <header class="page-head">
      <div>
        <span class="page-kicker">COMMUNITY MODERATION</span>
        <h1 class="page-title">评论管理</h1>
        <p class="page-subtitle">查看社区讨论上下文，及时处理不适当内容。</p>
      </div>
      <div class="page-actions"><el-button :icon="Refresh" @click="load">刷新</el-button></div>
    </header>

    <section class="filter-bar">
      <el-input v-model="filters.search" class="grow" clearable placeholder="搜索评论、作者或博客标题" :prefix-icon="Search" @keyup.enter="search" />
      <el-button type="primary" :icon="Search" @click="search">查询</el-button>
      <el-button @click="filters.search = ''; search()">重置</el-button>
    </section>

    <section class="panel">
      <div class="panel-head">
        <div><h2 class="panel-title">社区评论</h2><span class="panel-note">共 {{ total }} 条评论</span></div>
        <el-button v-if="selected.length" type="danger" plain :icon="Delete" @click="bulkRemove">删除所选</el-button>
      </div>
      <el-table v-loading="loading" :data="rows" row-key="id" @selection-change="selected = $event">
        <el-table-column type="selection" width="48" />
        <el-table-column label="评论内容" min-width="310">
          <template #default="{ row }">
            <div class="comment-cell"><el-icon><ChatDotRound /></el-icon><span>{{ row.content }}</span></div>
          </template>
        </el-table-column>
        <el-table-column label="评论者" width="165">
          <template #default="{ row }">
            <div class="person">
              <el-avatar :size="34" :src="row.author.avatar">{{ row.author.username.slice(0, 1) }}</el-avatar>
              <span class="person-meta"><strong class="person-name">{{ row.author.username }}</strong><small class="person-sub">{{ row.author.email || '未设置邮箱' }}</small></span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="所属博客" min-width="190" show-overflow-tooltip prop="blog_title" />
        <el-table-column label="点赞" width="75" align="center" prop="total_likes" />
        <el-table-column label="时间" width="170">
          <template #default="{ row }">{{ formatDate(row.pub_time) }}</template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="120" align="right">
          <template #default="{ row }">
            <el-button link :icon="View" @click="showDetail(row)">查看</el-button>
            <el-button link type="danger" :icon="Delete" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="table-footer">
        <span class="selection-note">{{ selected.length ? `已选择 ${selected.length} 项` : '删除操作不可撤销' }}</span>
        <el-pagination v-model:current-page="filters.page" v-model:page-size="filters.page_size" background layout="total, sizes, prev, pager, next" :total="total" :page-sizes="[10, 15, 30, 50]" @change="load" />
      </div>
    </section>

    <el-drawer v-model="detailOpen" title="评论详情" size="min(520px, 94vw)">
      <div v-if="detail" class="detail-card">
        <div class="person detail-person">
          <el-avatar :size="46" :src="detail.author.avatar">{{ detail.author.username.slice(0, 1) }}</el-avatar>
          <span class="person-meta"><strong class="person-name">{{ detail.author.username }}</strong><small class="person-sub">{{ formatDate(detail.pub_time) }}</small></span>
        </div>
        <div class="comment-content">{{ detail.content }}</div>
        <dl>
          <div><dt>所属博客</dt><dd>{{ detail.blog_title }}</dd></div>
          <div><dt>点赞数</dt><dd>{{ detail.total_likes }}</dd></div>
          <div v-if="detail.parent"><dt>回复评论</dt><dd>{{ detail.parent_content || `评论 #${detail.parent}` }}</dd></div>
        </dl>
        <el-button type="danger" plain :icon="Delete" @click="remove(detail); detailOpen = false">删除这条评论</el-button>
      </div>
    </el-drawer>
  </div>
</template>

<style scoped>
.comment-cell { display: flex; align-items: flex-start; gap: 10px; padding: 5px 0; }
.comment-cell .el-icon { flex: none; margin-top: 2px; color: var(--cyan-600); }
.comment-cell span { display: -webkit-box; overflow: hidden; color: var(--ink-700); font-size: 12px; line-height: 1.6; -webkit-box-orient: vertical; -webkit-line-clamp: 2; }
.detail-card { padding: 4px 8px; }
.detail-person { padding-bottom: 20px; border-bottom: 1px solid var(--silver-100); }
.comment-content { margin: 22px 0; padding: 20px; border-radius: 14px; background: var(--silver-50); font-size: 14px; line-height: 1.9; white-space: pre-wrap; }
dl { display: grid; gap: 1px; margin: 0 0 24px; overflow: hidden; border: 1px solid var(--silver-200); border-radius: 12px; background: var(--silver-200); }
dl div { display: grid; grid-template-columns: 90px 1fr; gap: 12px; padding: 12px; background: #fff; }
dt { color: var(--ink-500); font-size: 11px; }
dd { margin: 0; font-size: 12px; line-height: 1.6; }
</style>

