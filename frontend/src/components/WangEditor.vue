<script setup lang="ts">
import '@wangeditor/editor/dist/css/style.css'

import { computed, nextTick, onBeforeUnmount, ref, shallowRef, watch } from 'vue'
import { Editor, Toolbar } from '@wangeditor/editor-for-vue'
import type { IDomEditor, IEditorConfig, IToolbarConfig } from '@wangeditor/editor'
import { ElMessage } from 'element-plus'
import { Picture, UploadFilled } from '@element-plus/icons-vue'

import { blogApi } from '@/api/blog'

export interface EditorUploadState {
  name: string
  progress: number
  status: 'uploading' | 'success' | 'error'
  message?: string
}

const props = defineProps<{ modelValue: string }>()
const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'upload-state', value: EditorUploadState): void
}>()

const editorRef = shallowRef<IDomEditor>()
const fileInputRef = ref<HTMLInputElement>()
const dragging = ref(false)
let toolbarInsertFn: ((url: string, alt?: string, href?: string) => void) | null = null
const html = ref(props.modelValue)
const isEmpty = computed(() => {
  const text = html.value.replace(/<[^>]*>/g, '').replace(/&nbsp;/g, ' ').trim()
  return !text && !/<img\b/i.test(html.value)
})

watch(() => props.modelValue, (value) => {
  if (value !== html.value) html.value = value
})
watch(html, (value) => emit('update:modelValue', value))

const toolbarConfig: Partial<IToolbarConfig> = {
  excludeKeys: ['group-video'],
}

const editorConfig: Partial<IEditorConfig> = {
  placeholder: '开始写作，让想法在这里慢慢成形…',
  MENU_CONF: {
    uploadImage: {
      maxFileSize: 10 * 1024 * 1024,
      maxNumberOfFiles: 10,
      allowedFileTypes: ['image/*'],
      customBrowseAndUpload(insertFn: (url: string, alt?: string, href?: string) => void) {
        toolbarInsertFn = insertFn
        openFilePicker()
      },
      async customUpload(file: File, insertFn: (url: string, alt?: string, href?: string) => void) {
        await uploadFile(file, insertFn)
      },
    },
  },
}

function onCreated(editor: IDomEditor) {
  editorRef.value = editor
}

function openFilePicker() {
  fileInputRef.value?.click()
}

function validateImage(file: File) {
  const allowedTypes = new Set([
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/webp',
    'image/bmp',
  ])
  if (!allowedTypes.has(file.type)) return '仅支持 JPG、PNG、GIF、WebP、BMP 图片'
  if (file.size > 10 * 1024 * 1024) return '图片大小不能超过 10MB'
  return ''
}

function escapeAttribute(value: string) {
  return value
    .replace(/&/g, '&amp;')
    .replace(/"/g, '&quot;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
}

function insertUploadedImage(url: string, alt: string) {
  const editor = editorRef.value
  if (!editor) {
    ElMessage.error('编辑器尚未准备好，请稍后重试')
    return
  }
  editor.focus()
  editor.dangerouslyInsertHtml(
    `<p><img src="${escapeAttribute(url)}" alt="${escapeAttribute(alt)}" /></p>`,
  )
}

async function uploadFile(
  file: File,
  insertFn?: (url: string, alt?: string, href?: string) => void,
) {
  const validationMessage = validateImage(file)
  if (validationMessage) {
    emit('upload-state', {
      name: file.name,
      progress: 0,
      status: 'error',
      message: validationMessage,
    })
    ElMessage.warning(validationMessage)
    return
  }

  const state: EditorUploadState = { name: file.name, progress: 0, status: 'uploading' }
  emit('upload-state', state)
  try {
    const result = await blogApi.uploadEditorImage(file, (progress) => {
      state.progress = progress
      emit('upload-state', { ...state })
    })
    if (insertFn) insertFn(result.url, result.alt || file.name, result.href || '')
    else insertUploadedImage(result.url, result.alt || file.name)
    emit('upload-state', { name: file.name, progress: 100, status: 'success' })
    ElMessage.success(`图片“${file.name}”上传成功`)
  } catch (error: any) {
    const message = error?.response?.data?.message
      || error?.response?.data?.detail
      || error?.message
      || '图片上传失败，请稍后重试'
    emit('upload-state', { name: file.name, progress: state.progress, status: 'error', message })
    ElMessage.error(message)
  }
}

async function uploadFiles(files: FileList | File[]) {
  const images = Array.from(files).filter((file) => file.type.startsWith('image/'))
  if (!images.length) {
    ElMessage.warning('请选择图片文件')
    return
  }
  const insertFn = toolbarInsertFn
  toolbarInsertFn = null
  for (const file of images) {
    await uploadFile(file, insertFn || undefined)
  }
  if (fileInputRef.value) fileInputRef.value.value = ''
}

function onFileChange(event: Event) {
  const input = event.target as HTMLInputElement
  if (input.files?.length) void uploadFiles(input.files)
}

function onDragEnter(event: DragEvent) {
  if (event.dataTransfer?.types.includes('Files')) dragging.value = true
}

function onDragLeave(event: DragEvent) {
  const current = event.currentTarget as HTMLElement
  const next = event.relatedTarget as Node | null
  if (!next || !current.contains(next)) dragging.value = false
}

function onDrop(event: DragEvent) {
  dragging.value = false
  if (event.dataTransfer?.files.length) void uploadFiles(event.dataTransfer.files)
}

function onPaste(event: ClipboardEvent) {
  const files = Array.from(event.clipboardData?.files || [])
  const images = files.filter((file) => file.type.startsWith('image/'))
  if (!images.length) return
  event.preventDefault()
  void uploadFiles(images)
}

async function focusEditor() {
  await nextTick()
  editorRef.value?.focus()
}

onBeforeUnmount(() => editorRef.value?.destroy())
</script>

<template>
  <div
    class="editor-shell"
    :class="{ 'is-dragging': dragging }"
    @dragenter.prevent="onDragEnter"
    @dragover.prevent
    @dragleave.prevent="onDragLeave"
    @drop.capture.prevent.stop="onDrop"
    @paste.capture="onPaste"
  >
    <input
      ref="fileInputRef"
      class="file-input"
      type="file"
      accept=".jpg,.jpeg,.png,.gif,.webp,.bmp,image/jpeg,image/png,image/gif,image/webp,image/bmp"
      multiple
      @change="onFileChange"
    />
    <div class="editor-commandbar">
      <Toolbar :editor="editorRef" :default-config="toolbarConfig" mode="default" class="editor-toolbar" />
      <button class="local-upload-button" type="button" @click="openFilePicker">
        <el-icon><Picture /></el-icon>
        上传本地图片
      </button>
    </div>
    <div class="editor-body" @click="focusEditor">
      <Editor
        v-model="html"
        :default-config="editorConfig"
        mode="default"
        class="editor-area"
        @on-created="onCreated"
      />
      <div v-if="isEmpty || dragging" class="empty-hint" :class="{ active: dragging }" aria-hidden="true">
        <el-icon><UploadFilled /></el-icon>
        <strong>{{ dragging ? '松开鼠标即可上传图片' : '开始写作，或将图片拖到这里' }}</strong>
        <span>支持粘贴图片（Ctrl + V），也可以点击“上传本地图片”</span>
        <small>JPG、PNG、GIF、WebP、BMP · 单张不超过 10MB</small>
      </div>
    </div>
    <footer class="editor-footer">
      <span>正文至少 10 个字</span>
      <span>图片支持拖拽、粘贴和本地选择</span>
    </footer>
  </div>
</template>

<style scoped>
.editor-shell {
  overflow: hidden;
  border: 1px solid var(--silver-200);
  border-radius: 12px;
  background: var(--white);
  transition: border-color .2s ease, box-shadow .2s ease;
}
.editor-shell:focus-within {
  border-color: var(--cyan-500);
  box-shadow: 0 0 0 3px rgba(18, 173, 186, .1);
}
.editor-shell.is-dragging {
  border-color: var(--cyan-500);
  box-shadow: 0 0 0 4px rgba(18, 173, 186, .12);
}
.file-input {
  position: fixed;
  width: 1px;
  height: 1px;
  overflow: hidden;
  opacity: 0;
  pointer-events: none;
}
.editor-commandbar {
  display: flex;
  align-items: stretch;
  border-bottom: 1px solid var(--silver-200);
  background: #fbfcfc;
}
.editor-toolbar {
  position: relative;
  z-index: 2;
  flex: 1;
  min-width: 0;
  background: #fbfcfc;
}
.local-upload-button {
  display: flex;
  flex: none;
  align-items: center;
  gap: 6px;
  margin: 6px 8px 6px 0;
  padding: 0 12px;
  border: 1px solid var(--cyan-500);
  border-radius: 7px;
  background: var(--cyan-50);
  color: var(--cyan-700);
  cursor: pointer;
  font-size: .76rem;
  font-weight: 700;
}
.local-upload-button:hover {
  background: var(--cyan-100);
}
.editor-body { position: relative; min-height: 500px; }
.editor-area { min-height: 500px; overflow-y: auto; }
.empty-hint {
  position: absolute;
  inset: 118px 12% auto;
  display: grid;
  justify-items: center;
  padding: 42px 28px;
  border: 1px dashed var(--silver-300);
  border-radius: 14px;
  color: var(--silver-500);
  text-align: center;
  pointer-events: none;
}
.empty-hint.active {
  z-index: 3;
  border-color: var(--cyan-500);
  background: rgba(239, 251, 252, .96);
}
.empty-hint .el-icon { margin-bottom: 14px; color: var(--cyan-600); font-size: 2.5rem; }
.empty-hint strong { color: var(--silver-900); font-size: 1rem; }
.empty-hint span { margin-top: 10px; font-size: .84rem; }
.empty-hint small { margin-top: 8px; color: var(--cyan-700); font-size: .76rem; }
.editor-footer {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 16px;
  border-top: 1px solid var(--silver-100);
  color: var(--silver-500);
  font-size: .75rem;
}
:deep(.w-e-text-container) { background: var(--white); }
:deep(.w-e-text-placeholder) { top: 24px; color: var(--silver-300); font-style: normal; }
:deep(.w-e-text) {
  min-height: 500px;
  padding: 24px 28px;
  color: var(--silver-900);
  font-size: 16px;
  line-height: 1.85;
}
:deep([data-menu-key="uploadImage"]) { color: var(--cyan-700) !important; }
@media (max-width: 720px) {
  .editor-commandbar { display: block; }
  .local-upload-button {
    min-height: 36px;
    margin: 0 10px 9px auto;
  }
  .editor-body, .editor-area, :deep(.w-e-text) { min-height: 420px; }
  .empty-hint { inset: 105px 18px auto; padding: 32px 18px; }
  .editor-footer { flex-direction: column; gap: 3px; }
}
</style>
