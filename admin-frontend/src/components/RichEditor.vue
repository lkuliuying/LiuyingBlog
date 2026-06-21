<script setup lang="ts">
import '@wangeditor/editor/dist/css/style.css'

import { onBeforeUnmount, shallowRef } from 'vue'
import type { IDomEditor, IEditorConfig, IToolbarConfig } from '@wangeditor/editor'
import { Editor, Toolbar } from '@wangeditor/editor-for-vue'
import { ElMessage } from 'element-plus'

import { adminApi } from '@/api/admin'

const props = defineProps<{ modelValue: string }>()
const emit = defineEmits<{ (event: 'update:modelValue', value: string): void }>()
const editorRef = shallowRef<IDomEditor>()

const toolbarConfig: Partial<IToolbarConfig> = {
  excludeKeys: ['group-video'],
}
const editorConfig: Partial<IEditorConfig> = {
  placeholder: '输入博客正文，支持图文混排…',
  MENU_CONF: {
    uploadImage: {
      maxFileSize: 10 * 1024 * 1024,
      allowedFileTypes: ['image/*'],
      async customUpload(file: File, insertFn: (url: string, alt?: string, href?: string) => void) {
        try {
          const result = await adminApi.uploadImage(file)
          insertFn(result.url, result.alt || file.name, result.href || '')
        } catch {
          ElMessage.error('图片上传失败')
        }
      },
    },
  },
}

function created(editor: IDomEditor) {
  editorRef.value = editor
}

onBeforeUnmount(() => editorRef.value?.destroy())
</script>

<template>
  <div class="rich-editor">
    <Toolbar :editor="editorRef" :default-config="toolbarConfig" mode="default" class="toolbar" />
    <Editor
      :model-value="props.modelValue"
      :default-config="editorConfig"
      mode="default"
      class="editor"
      @update:model-value="emit('update:modelValue', $event)"
      @on-created="created"
    />
  </div>
</template>

<style scoped>
.rich-editor { overflow: hidden; border: 1px solid var(--silver-200); border-radius: 12px; }
.rich-editor:focus-within { border-color: var(--cyan-500); box-shadow: 0 0 0 3px var(--cyan-100); }
.toolbar { border-bottom: 1px solid var(--silver-200); background: #f9fbfb; }
.editor { min-height: 330px; overflow-y: auto; }
:deep(.w-e-text-container) { min-height: 330px; background: #fff; }
:deep(.w-e-text) { min-height: 330px; padding: 20px 22px; font-size: 15px; line-height: 1.8; }
</style>

