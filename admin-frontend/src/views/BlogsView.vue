<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { Delete, Edit, Plus, Refresh, Search, View } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'

import { adminApi } from '@/api/admin'
import RichEditor from '@/components/RichEditor.vue'
import type { AdminBlog, Category } from '@/types'
import { formatDate } from '@/utils/format'

const loading = ref(false)
const saving = ref(false)
const rows = ref<AdminBlog[]>([])
const categories = ref<Category[]>([])
const selected = ref<AdminBlog[]>([])
const total = ref(0)
const editorOpen = ref(false)
const previewOpen = ref(false)
const previewBlog = ref<AdminBlog | null>(null)
const formRef = ref<FormInstance>()
const filters = reactive({
  page: 1,
  page_size: 15,
  search: '',
  category: '',
  ordering: '-pub_time',
  dates: [] as string[],
})
const form = reactive({
  id: undefined as number | undefined,
  title: '',
  category_id: undefined as number | undefined,
  content: '',
})
const rules: FormRules = {
  title: [
    { required: true, message: '请输入博客标题', trigger: 'blur' },
    { min: 2, max: 200, message: '标题长度为 2—200 个字符', trigger: 'blur' },
  ],
  category_id: [{ required: true, message: '请选择分类', trigger: 'change' }],
  content: [{ required: true, message: '请输入博客正文', trigger: 'change' }],
}

async function load() {
  loading.value = true
  try {
    const result = await adminApi.blogs({
      page: filters.page,
      page_size: filters.page_size,
      search: filters.search || undefined,
      category: filters.category || undefined,
      ordering: filters.ordering,
      date_from: filters.dates?.[0],
      date_to: filters.dates?.[1],
    })
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

function reset() {
  Object.assign(filters, { page: 1, search: '', category: '', ordering: '-pub_time', dates: [] })
  load()
}

function openCreate() {
  Object.assign(form, { id: undefined, title: '', category_id: undefined, content: '' })
  editorOpen.value = true
}

async function openEdit(blog: AdminBlog) {
  loading.value = true
  try {
    const detail = await adminApi.blog(blog.id)
    Object.assign(form, {
      id: detail.id,
      title: detail.title,
      category_id: detail.category?.id,
      content: detail.content,
    })
    editorOpen.value = true
  } finally {
    loading.value = false
  }
}

async function openPreview(blog: AdminBlog) {
  loading.value = true
  try {
    previewBlog.value = await adminApi.blog(blog.id)
    previewOpen.value = true
  } finally {
    loading.value = false
  }
}

async function save() {
  await formRef.value?.validate()
  if (!form.category_id) return
  saving.value = true
  try {
    await adminApi.saveBlog({
      id: form.id,
      title: form.title,
      content: form.content,
      category_id: form.category_id,
    })
    ElMessage.success(form.id ? '博客已更新' : '博客已创建')
    editorOpen.value = false
    await load()
  } finally {
    saving.value = false
  }
}

async function remove(blog: AdminBlog) {
  await ElMessageBox.confirm(`确定删除《${blog.title}》吗？相关评论也会一并删除。`, '删除博客', {
    confirmButtonText: '确认删除',
    cancelButtonText: '取消',
    type: 'warning',
  })
  await adminApi.deleteBlog(blog.id)
  ElMessage.success('博客已删除')
  await load()
}

async function bulkRemove() {
  if (!selected.value.length) return
  await ElMessageBox.confirm(`确定删除选中的 ${selected.value.length} 篇博客吗？`, '批量删除', {
    confirmButtonText: '确认删除',
    cancelButtonText: '取消',
    type: 'warning',
  })
  await adminApi.bulkDeleteBlogs(selected.value.map((item) => item.id))
  ElMessage.success('已完成批量删除')
  await load()
}

onMounted(async () => {
  categories.value = await adminApi.categories()
  await load()
})
</script>

<template>
  <div>
    <header class="page-head">
      <div>
        <span class="page-kicker">CONTENT LIBRARY</span>
        <h1 class="page-title">博客管理</h1>
        <p class="page-subtitle">检索、编辑和维护社区中的全部博客内容。</p>
      </div>
      <div class="page-actions">
        <el-button :icon="Refresh" @click="load">刷新</el-button>
        <el-button type="primary" :icon="Plus" @click="openCreate">新建博客</el-button>
      </div>
    </header>

    <section class="filter-bar">
      <el-input v-model="filters.search" class="grow" clearable placeholder="搜索标题、正文或作者" :prefix-icon="Search" @keyup.enter="search" />
      <el-select v-model="filters.category" clearable placeholder="全部分类" style="width: 160px" @change="search">
        <el-option v-for="category in categories" :key="category.id" :label="category.name" :value="category.id" />
      </el-select>
      <el-date-picker v-model="filters.dates" type="daterange" value-format="YYYY-MM-DD" start-placeholder="开始日期" end-placeholder="结束日期" style="width: 240px" />
      <el-select v-model="filters.ordering" style="width: 150px" @change="search">
        <el-option label="最新发布" value="-pub_time" />
        <el-option label="最早发布" value="pub_time" />
        <el-option label="最近更新" value="-updated_time" />
      </el-select>
      <el-button type="primary" :icon="Search" @click="search">查询</el-button>
      <el-button @click="reset">重置</el-button>
    </section>

    <section class="panel">
      <div class="panel-head">
        <div><h2 class="panel-title">博客内容库</h2><span class="panel-note">共 {{ total }} 篇博客</span></div>
        <el-button v-if="selected.length" type="danger" plain :icon="Delete" @click="bulkRemove">删除所选</el-button>
      </div>
      <el-table v-loading="loading" :data="rows" row-key="id" @selection-change="selected = $event">
        <el-table-column type="selection" width="48" />
        <el-table-column label="博客" min-width="300">
          <template #default="{ row }">
            <div class="blog-cell">
              <strong>{{ row.title }}</strong>
              <span>{{ row.summary || '暂无摘要' }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="作者" min-width="150">
          <template #default="{ row }">
            <div class="person">
              <el-avatar :size="34" :src="row.author.avatar">{{ row.author.username.slice(0, 1) }}</el-avatar>
              <span class="person-meta"><strong class="person-name">{{ row.author.username }}</strong><small class="person-sub">{{ row.author.email || '未设置邮箱' }}</small></span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="分类" width="120">
          <template #default="{ row }"><el-tag effect="plain">{{ row.category?.name || '未分类' }}</el-tag></template>
        </el-table-column>
        <el-table-column label="互动" width="130">
          <template #default="{ row }"><span class="interaction">{{ row.total_likes }} 赞 · {{ row.total_collections }} 藏</span></template>
        </el-table-column>
        <el-table-column label="发布时间" width="170">
          <template #default="{ row }">{{ formatDate(row.pub_time) }}</template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="150" align="right">
          <template #default="{ row }">
            <el-button link :icon="View" @click="openPreview(row)">预览</el-button>
            <el-button link type="primary" :icon="Edit" @click="openEdit(row)">编辑</el-button>
            <el-button link type="danger" :icon="Delete" @click="remove(row)" />
          </template>
        </el-table-column>
      </el-table>
      <div class="table-footer">
        <span class="selection-note">{{ selected.length ? `已选择 ${selected.length} 项` : '可勾选后批量操作' }}</span>
        <el-pagination
          v-model:current-page="filters.page"
          v-model:page-size="filters.page_size"
          background
          layout="total, sizes, prev, pager, next"
          :total="total"
          :page-sizes="[10, 15, 30, 50]"
          @change="load"
        />
      </div>
    </section>

    <el-dialog v-model="editorOpen" :title="form.id ? '编辑博客' : '新建博客'" width="min(960px, 94vw)" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <div class="editor-fields">
          <el-form-item label="博客标题" prop="title">
            <el-input v-model="form.title" maxlength="200" show-word-limit placeholder="输入清晰、准确的博客标题" />
          </el-form-item>
          <el-form-item label="内容分类" prop="category_id">
            <el-select v-model="form.category_id" placeholder="选择分类">
              <el-option v-for="category in categories" :key="category.id" :label="category.name" :value="category.id" />
            </el-select>
          </el-form-item>
        </div>
        <el-form-item label="博客正文" prop="content">
          <RichEditor v-model="form.content" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editorOpen = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">{{ form.id ? '保存修改' : '发布博客' }}</el-button>
      </template>
    </el-dialog>

    <el-drawer v-model="previewOpen" title="博客预览" size="min(760px, 94vw)">
      <article v-if="previewBlog" class="preview">
        <span class="page-kicker">{{ previewBlog.category?.name || '未分类' }}</span>
        <h2>{{ previewBlog.title }}</h2>
        <div class="preview-meta">{{ previewBlog.author.username }} · {{ formatDate(previewBlog.pub_time) }}</div>
        <div class="preview-content" v-html="previewBlog.content" />
      </article>
    </el-drawer>
  </div>
</template>

<style scoped>
.blog-cell { display: grid; min-width: 0; gap: 5px; padding: 4px 0; }
.blog-cell strong { overflow: hidden; color: var(--ink-900); font-size: 13px; text-overflow: ellipsis; white-space: nowrap; }
.blog-cell span { overflow: hidden; color: var(--ink-500); font-size: 11px; text-overflow: ellipsis; white-space: nowrap; }
.interaction { color: var(--ink-500); font-size: 11px; white-space: nowrap; }
.editor-fields { display: grid; grid-template-columns: minmax(0,1fr) 220px; gap: 16px; }
.editor-fields :deep(.el-select) { width: 100%; }
.preview { padding: 4px 12px 40px; }
.preview h2 { margin: 8px 0 12px; font-size: 30px; line-height: 1.3; letter-spacing: -.04em; }
.preview-meta { padding-bottom: 18px; border-bottom: 1px solid var(--silver-100); color: var(--ink-500); font-size: 12px; }
.preview-content { margin-top: 24px; color: var(--ink-900); font-size: 15px; line-height: 1.85; }
.preview-content :deep(img) { max-width: 100%; height: auto; border-radius: 10px; }
@media (max-width: 700px) { .editor-fields { grid-template-columns: 1fr; } }
</style>

