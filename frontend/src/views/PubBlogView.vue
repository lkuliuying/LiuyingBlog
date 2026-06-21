<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { CircleCheck, CircleClose, DocumentChecked, InfoFilled, Loading, Picture, Promotion } from '@element-plus/icons-vue'

import { blogApi } from '@/api/blog'
import WangEditor from '@/components/WangEditor.vue'
import type { EditorUploadState } from '@/components/WangEditor.vue'
import type { BlogCategory } from '@/types'

const router = useRouter()
const formRef = ref<FormInstance>()
const submitting = ref(false)
const loadingCategories = ref(false)
const categories = ref<BlogCategory[]>([])
const lastUpload = ref<EditorUploadState | null>(null)
const draftState = ref<'idle' | 'saving' | 'saved'>('idle')
const DRAFT_KEY = 'liuying.blog-draft'
let saveTimer: ReturnType<typeof setTimeout> | undefined

const form = reactive({
  title: '',
  content: '',
  category: undefined as number | undefined,
})

const plainContent = computed(() => form.content
  .replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '')
  .replace(/<script[^>]*>[\s\S]*?<\/script>/gi, '')
  .replace(/<[^>]+>/g, ' ')
  .replace(/&nbsp;|&#160;/gi, ' ')
  .replace(/&[a-z]+;/gi, ' ')
  .replace(/\s+/g, ' ')
  .trim())
const titleReady = computed(() => form.title.trim().length >= 2)
const contentReady = computed(() => plainContent.value.length >= 10)
const categoryReady = computed(() => typeof form.category === 'number')
const canPublish = computed(() =>
  titleReady.value && contentReady.value && categoryReady.value && lastUpload.value?.status !== 'uploading')

const rules: FormRules = {
  title: [
    { required: true, message: '标题不能为空', trigger: 'blur' },
    { min: 2, max: 200, message: '标题长度应在 2–200 个字符之间', trigger: 'blur' },
  ],
  category: [{ required: true, message: '请选择文章分类', trigger: 'change' }],
  content: [{
    validator: (_rule, _value, callback) => {
      if (!plainContent.value) callback(new Error('正文不能为空'))
      else if (plainContent.value.length < 10) callback(new Error('正文至少需要 10 个字'))
      else callback()
    },
    trigger: 'change',
  }],
}

async function loadCategories() {
  loadingCategories.value = true
  try {
    categories.value = await blogApi.categories()
  } finally {
    loadingCategories.value = false
  }
}

function restoreDraft() {
  const raw = localStorage.getItem(DRAFT_KEY)
  if (!raw) return
  try {
    const draft = JSON.parse(raw)
    form.title = typeof draft.title === 'string' ? draft.title : ''
    form.content = typeof draft.content === 'string' ? draft.content : ''
    form.category = typeof draft.category === 'number' ? draft.category : undefined
    if (form.title || form.content) ElMessage.info('已恢复上次未发布的内容')
  } catch {
    localStorage.removeItem(DRAFT_KEY)
  }
}

function scheduleDraftSave() {
  draftState.value = 'saving'
  clearTimeout(saveTimer)
  saveTimer = setTimeout(() => {
    localStorage.setItem(DRAFT_KEY, JSON.stringify(form))
    draftState.value = 'saved'
  }, 600)
}

async function submit() {
  if (!formRef.value || submitting.value) return
  if (lastUpload.value?.status === 'uploading') {
    ElMessage.warning('请等待图片上传完成后再发布')
    return
  }
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) {
    ElMessage.warning('请先完成右侧标出的必填内容')
    return
  }
  submitting.value = true
  try {
    const blog = await blogApi.create({
      title: form.title.trim(),
      content: form.content,
      category: form.category as number,
    })
    localStorage.removeItem(DRAFT_KEY)
    ElMessage.success('博客发布成功')
    router.push({ name: 'blog-detail', params: { id: blog.id } })
  } finally {
    submitting.value = false
  }
}

watch(form, scheduleDraftSave, { deep: true })
onMounted(() => {
  restoreDraft()
  loadCategories()
})
onBeforeUnmount(() => clearTimeout(saveTimer))
</script>

<template>
  <section class="publish-page">
    <header class="publish-heading">
      <div>
        <span class="eyebrow">CREATOR STUDIO</span>
        <h1>发布博客</h1>
        <p>让好内容被看见，也让每一次表达都有落点。</p>
      </div>
      <div class="draft-state" :class="draftState">
        <el-icon v-if="draftState === 'saving'" class="is-loading"><Loading /></el-icon>
        <el-icon v-else><DocumentChecked /></el-icon>
        {{ draftState === 'saving' ? '正在保存草稿' : draftState === 'saved' ? '草稿已保存到本地' : '内容会自动保存' }}
      </div>
    </header>

    <el-form ref="formRef" :model="form" :rules="rules" class="publish-grid">
      <main class="writing-column">
        <el-form-item prop="title" class="title-field">
          <template #label>
            <div class="field-label">
              <span><b>*</b> 文章标题</span>
              <small>{{ form.title.length }}/200</small>
            </div>
          </template>
          <el-input v-model="form.title" maxlength="200" placeholder="给你的文章起一个清晰、有吸引力的标题" class="title-input" />
        </el-form-item>

        <el-form-item prop="content" class="content-field">
          <template #label>
            <div class="field-label">
              <span><b>*</b> 正文内容</span>
              <small>{{ plainContent.length }} 字</small>
            </div>
          </template>
          <WangEditor v-model="form.content" @upload-state="lastUpload = $event" />
        </el-form-item>
      </main>

      <aside class="publish-sidebar">
        <div class="sidebar-section">
          <div class="sidebar-title">
            <div><span class="sidebar-kicker">PUBLISH</span><h2>发布设置</h2></div>
            <el-icon><DocumentChecked /></el-icon>
          </div>
          <el-form-item label="选择分类" prop="category" class="category-field">
            <el-select v-model="form.category" :loading="loadingCategories" placeholder="请选择文章分类" size="large" style="width: 100%">
              <el-option v-for="category in categories" :key="category.id" :label="category.name" :value="category.id" />
            </el-select>
          </el-form-item>
        </div>

        <div class="sidebar-section">
          <h3>内容检查</h3>
          <div class="check-list">
            <div :class="{ ready: titleReady }">
              <el-icon><CircleCheck v-if="titleReady" /><CircleClose v-else /></el-icon>
              <span><strong>文章标题</strong><small>{{ titleReady ? '标题已填写' : '至少填写 2 个字符' }}</small></span>
            </div>
            <div :class="{ ready: contentReady }">
              <el-icon><CircleCheck v-if="contentReady" /><CircleClose v-else /></el-icon>
              <span><strong>正文内容</strong><small>{{ contentReady ? `已有 ${plainContent.length} 个字` : '正文至少需要 10 个字' }}</small></span>
            </div>
            <div :class="{ ready: categoryReady }">
              <el-icon><CircleCheck v-if="categoryReady" /><CircleClose v-else /></el-icon>
              <span><strong>文章分类</strong><small>{{ categoryReady ? '分类已选择' : '请选择一个分类' }}</small></span>
            </div>
          </div>
        </div>

        <div class="sidebar-section">
          <div class="upload-heading">
            <el-icon><Picture /></el-icon>
            <div><h3>本地图片上传</h3><p>拖拽、粘贴或点击编辑器图片按钮</p></div>
          </div>
          <div v-if="lastUpload" class="upload-state" :class="lastUpload.status">
            <div class="upload-file">
              <el-icon v-if="lastUpload.status === 'uploading'" class="is-loading"><Loading /></el-icon>
              <el-icon v-else-if="lastUpload.status === 'success'"><CircleCheck /></el-icon>
              <el-icon v-else><CircleClose /></el-icon>
              <span>
                <strong>{{ lastUpload.name }}</strong>
                <small>{{ lastUpload.status === 'uploading' ? `上传中 ${lastUpload.progress}%` : lastUpload.status === 'success' ? '已插入正文' : lastUpload.message }}</small>
              </span>
            </div>
            <el-progress v-if="lastUpload.status === 'uploading'" :percentage="lastUpload.progress" :show-text="false" :stroke-width="4" />
          </div>
          <div class="upload-note">
            <el-icon><InfoFilled /></el-icon>
            <span>支持 JPG、PNG、GIF、WebP、BMP，单张不超过 10MB。</span>
          </div>
        </div>

        <div class="publish-actions">
          <el-button type="primary" size="large" :loading="submitting" :disabled="!canPublish" @click="submit">
            <el-icon><Promotion /></el-icon>发布文章
          </el-button>
          <small>{{ canPublish ? '内容已就绪，可以发布了' : '完成标题、正文和分类后即可发布' }}</small>
        </div>
      </aside>
    </el-form>
  </section>
</template>

<style scoped>
.publish-page { width: min(100% - 48px, 1440px); margin: 0 auto; padding: 44px 0 72px; }
.publish-heading { display: flex; align-items: flex-end; justify-content: space-between; gap: 24px; margin-bottom: 30px; }
.eyebrow,.sidebar-kicker { color: var(--cyan-700); font-size: .68rem; font-weight: 800; letter-spacing: .16em; }
.publish-heading h1 { margin: 5px 0 8px; font-family: 'Noto Serif SC','Source Han Serif SC',serif; font-size: clamp(2rem,3vw,2.8rem); line-height: 1.1; letter-spacing: -.04em; }
.publish-heading p { margin: 0; color: var(--silver-500); font-size: .94rem; }
.draft-state { display: flex; align-items: center; gap: 7px; padding: 9px 12px; border: 1px solid var(--silver-200); border-radius: 999px; background: rgba(255,255,255,.72); color: var(--silver-500); font-size: .76rem; }
.draft-state.saved { color: #2f8f64; }
.publish-grid { display: grid; grid-template-columns: minmax(0,1fr) 326px; align-items: start; gap: 28px; }
.writing-column { min-width: 0; }
.field-label { display: flex; align-items: center; justify-content: space-between; width: 100%; color: var(--silver-900); font-size: .92rem; font-weight: 700; }
.field-label b { color: #d94d4d; }
.field-label small { color: var(--silver-500); font-size: .72rem; font-weight: 500; }
.title-input :deep(.el-input__wrapper) { min-height: 64px; padding: 0 20px; border-radius: 12px; box-shadow: 0 0 0 1px var(--silver-200) inset; }
.title-input :deep(.el-input__inner) { color: var(--silver-900); font-family: 'Noto Serif SC','Source Han Serif SC',serif; font-size: 1.22rem; font-weight: 600; }
.title-input :deep(.el-input__wrapper.is-focus) { box-shadow: 0 0 0 1px var(--cyan-500) inset,0 0 0 3px rgba(18,173,186,.1); }
.content-field { margin-bottom: 0; }
.content-field :deep(.el-form-item__content) { display: block; }
.publish-sidebar { position: sticky; top: 88px; overflow: hidden; border: 1px solid var(--silver-200); border-radius: 14px; background: rgba(255,255,255,.95); box-shadow: 0 14px 40px rgba(36,50,56,.06); }
.sidebar-section { padding: 22px; border-bottom: 1px solid var(--silver-100); }
.sidebar-title,.upload-heading { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; }
.sidebar-title > .el-icon { color: var(--cyan-600); font-size: 1.5rem; }
.sidebar-title h2 { margin: 4px 0 20px; font-family: 'Noto Serif SC','Source Han Serif SC',serif; font-size: 1.35rem; }
.category-field { margin-bottom: 0; }
.category-field :deep(.el-form-item__label) { color: var(--silver-700); font-size: .8rem; font-weight: 700; }
.sidebar-section h3 { margin: 0 0 16px; font-size: .92rem; }
.check-list { display: grid; gap: 15px; }
.check-list > div { display: flex; align-items: flex-start; gap: 10px; color: var(--silver-300); }
.check-list > div.ready { color: #32a56f; }
.check-list .el-icon { margin-top: 2px; font-size: 1rem; }
.check-list span,.upload-file span { display: grid; min-width: 0; }
.check-list strong,.upload-file strong { overflow: hidden; color: var(--silver-700); font-size: .8rem; text-overflow: ellipsis; white-space: nowrap; }
.check-list small,.upload-file small { margin-top: 2px; color: var(--silver-500); font-size: .7rem; }
.upload-heading { justify-content: flex-start; }
.upload-heading > .el-icon { display: grid; flex: 0 0 38px; width: 38px; height: 38px; place-items: center; border-radius: 10px; background: var(--cyan-50); color: var(--cyan-700); font-size: 1.15rem; }
.upload-heading h3 { margin: 0 0 4px; }
.upload-heading p { margin: 0; color: var(--silver-500); font-size: .7rem; line-height: 1.5; }
.upload-state { margin-top: 16px; padding: 12px; border: 1px solid var(--silver-200); border-radius: 10px; background: var(--silver-50); }
.upload-state.success { border-color: #bfe4d0; background: #f3fbf7; }
.upload-state.error { border-color: #f1c5c5; background: #fff7f7; }
.upload-file { display: flex; align-items: flex-start; gap: 9px; min-width: 0; }
.upload-state.uploading .upload-file > .el-icon { color: var(--cyan-600); }
.upload-state.success .upload-file > .el-icon { color: #32a56f; }
.upload-state.error .upload-file > .el-icon { color: #d94d4d; }
.upload-state :deep(.el-progress) { margin-top: 10px; }
.upload-note { display: flex; align-items: flex-start; gap: 7px; margin-top: 14px; color: var(--silver-500); font-size: .68rem; line-height: 1.6; }
.upload-note .el-icon { flex: none; margin-top: 2px; color: var(--cyan-600); }
.publish-actions { display: grid; gap: 9px; padding: 20px 22px 22px; }
.publish-actions .el-button { width: 100%; min-height: 44px; margin: 0; border: 0; border-radius: 10px; background: var(--cyan-600); font-weight: 800; box-shadow: 0 8px 20px rgba(7,150,165,.18); }
.publish-actions .el-button:not(.is-disabled):hover { background: var(--cyan-700); transform: translateY(-1px); }
.publish-actions small { color: var(--silver-500); text-align: center; font-size: .68rem; }
@media (max-width: 980px) {
  .publish-grid { grid-template-columns: 1fr; }
  .publish-sidebar { position: static; display: grid; grid-template-columns: repeat(2,1fr); }
  .publish-actions { grid-column: 1 / -1; }
}
@media (max-width: 720px) {
  .publish-page { width: min(100% - 24px,1440px); padding: 28px 0 48px; }
  .publish-heading { align-items: flex-start; flex-direction: column; margin-bottom: 22px; }
  .publish-grid { gap: 18px; }
  .publish-sidebar { grid-template-columns: 1fr; }
  .publish-actions { grid-column: auto; }
  .title-input :deep(.el-input__wrapper) { min-height: 56px; }
}
</style>
