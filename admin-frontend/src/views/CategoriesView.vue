<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { Delete, Edit, FolderAdd, Plus, Refresh } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'

import { adminApi } from '@/api/admin'
import type { Category } from '@/types'

const loading = ref(false)
const saving = ref(false)
const rows = ref<Category[]>([])
const dialogOpen = ref(false)
const formRef = ref<FormInstance>()
const form = reactive({ id: undefined as number | undefined, name: '' })
const rules: FormRules = {
  name: [{ required: true, message: '请输入分类名称', trigger: 'blur' }, { max: 20, message: '分类名称不能超过 20 个字符', trigger: 'blur' }],
}

async function load() {
  loading.value = true
  try {
    rows.value = await adminApi.categories()
  } finally {
    loading.value = false
  }
}

function openCreate() {
  Object.assign(form, { id: undefined, name: '' })
  dialogOpen.value = true
}

function openEdit(category: Category) {
  Object.assign(form, { id: category.id, name: category.name })
  dialogOpen.value = true
}

async function save() {
  await formRef.value?.validate()
  saving.value = true
  try {
    await adminApi.saveCategory(form)
    ElMessage.success(form.id ? '分类已更新' : '分类已创建')
    dialogOpen.value = false
    await load()
  } finally {
    saving.value = false
  }
}

async function remove(category: Category) {
  await ElMessageBox.confirm(`确定删除分类“${category.name}”吗？`, '删除分类', {
    confirmButtonText: '确认删除',
    cancelButtonText: '取消',
    type: 'warning',
  })
  await adminApi.deleteCategory(category.id)
  ElMessage.success('分类已删除')
  await load()
}

onMounted(load)
</script>

<template>
  <div>
    <header class="page-head">
      <div>
        <span class="page-kicker">CONTENT TAXONOMY</span>
        <h1 class="page-title">分类管理</h1>
        <p class="page-subtitle">维护内容结构，让社区知识更容易被发现。</p>
      </div>
      <div class="page-actions">
        <el-button :icon="Refresh" @click="load">刷新</el-button>
        <el-button type="primary" :icon="Plus" @click="openCreate">新建分类</el-button>
      </div>
    </header>

    <section v-loading="loading" class="category-grid">
      <article v-for="(category, index) in rows" :key="category.id" class="category-card">
        <div class="category-seq">{{ String(index + 1).padStart(2, '0') }}</div>
        <span class="category-icon"><el-icon><FolderAdd /></el-icon></span>
        <div class="category-copy"><h2>{{ category.name }}</h2><p>{{ category.blog_count }} 篇博客正在使用</p></div>
        <div class="category-actions">
          <el-button circle :icon="Edit" @click="openEdit(category)" />
          <el-button circle type="danger" plain :icon="Delete" :disabled="category.blog_count > 0" @click="remove(category)" />
        </div>
      </article>
      <button class="category-card add-card" type="button" @click="openCreate">
        <span class="category-icon"><el-icon><Plus /></el-icon></span>
        <div class="category-copy"><h2>创建新分类</h2><p>继续扩展社区内容结构</p></div>
      </button>
    </section>

    <div class="category-tip">
      <strong>删除保护</strong>
      <span>仍有关联博客的分类不能直接删除，请先在博客管理中调整内容分类。</span>
    </div>

    <el-dialog v-model="dialogOpen" :title="form.id ? '编辑分类' : '新建分类'" width="420px">
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="form.name" maxlength="20" show-word-limit placeholder="例如：Python、前端开发" @keyup.enter="save" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogOpen = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">保存分类</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.category-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; min-height: 150px; }
.category-card { position: relative; display: grid; grid-template-columns: auto 1fr auto; align-items: center; gap: 16px; min-height: 132px; padding: 22px; overflow: hidden; border: 1px solid var(--silver-200); border-radius: 16px; background: #fff; box-shadow: 0 8px 28px rgba(36,50,56,.04); text-align: left; transition: transform .18s ease, border-color .18s ease, box-shadow .18s ease; }
.category-card:hover { transform: translateY(-2px); border-color: var(--cyan-200); box-shadow: 0 14px 34px rgba(36,50,56,.075); }
.category-seq { position: absolute; top: 12px; right: 14px; color: var(--silver-100); font-size: 28px; font-weight: 900; letter-spacing: -.05em; }
.category-icon { display: grid; width: 46px; height: 46px; place-items: center; border-radius: 14px; background: var(--cyan-50); color: var(--cyan-700); font-size: 21px; }
.category-copy { min-width: 0; }
.category-copy h2 { margin: 0; font-size: 16px; }
.category-copy p { margin: 7px 0 0; color: var(--ink-500); font-size: 11px; }
.category-actions { position: relative; z-index: 2; display: flex; gap: 6px; }
.add-card { border-style: dashed; background: rgba(239,251,252,.48); color: inherit; cursor: pointer; }
.add-card .category-icon { border: 1px dashed var(--cyan-500); background: transparent; }
.category-tip { display: flex; gap: 14px; margin-top: 20px; padding: 16px 18px; border: 1px solid #f0ddbd; border-radius: 13px; background: #fffaf1; color: #8a672e; font-size: 12px; line-height: 1.6; }
@media (max-width: 1100px) { .category-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 650px) { .category-grid { grid-template-columns: 1fr; } .category-tip { flex-direction: column; gap: 4px; } }
</style>

