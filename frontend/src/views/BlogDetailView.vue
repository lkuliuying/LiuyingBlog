<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import hljs from 'highlight.js'
import 'highlight.js/styles/github-dark.min.css'

import { blogApi } from '@/api/blog'
import { commentApi } from '@/api/comment'
import CommentTree from '@/components/CommentTree.vue'
import type { BlogDetail, Comment } from '@/types'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const blog = ref<BlogDetail | null>(null)
const comments = ref<Comment[]>([])
const newComment = ref('')

const blogId = computed(() => route.params.id as string)

async function loadBlog() {
  blog.value = await blogApi.detail(blogId.value)
  await nextTick()
  document.querySelectorAll<HTMLElement>('.blog-content pre code').forEach((el) => {
    hljs.highlightElement(el)
  })
}

async function loadComments() {
  comments.value = await commentApi.listByBlog(blogId.value)
}

async function ensureLogin(action: string) {
  if (auth.isLogin) return true
  await ElMessageBox.confirm(`请先登录后再${action}`, '提示', {
    confirmButtonText: '去登录',
    cancelButtonText: '取消',
  }).then(() => router.push({ name: 'login', query: { next: route.fullPath } })).catch(() => {})
  return false
}

async function toggleLike() {
  if (!(await ensureLogin('点赞'))) return
  const data = await blogApi.toggleLike(blogId.value)
  if (blog.value) {
    blog.value.is_liked = data.is_liked
    blog.value.total_likes = data.total_likes
  }
}

async function toggleCollect() {
  if (!(await ensureLogin('收藏'))) return
  const data = await blogApi.toggleCollect(blogId.value)
  if (blog.value) {
    blog.value.is_collected = data.is_collected
    blog.value.total_collections = data.total_collections
  }
}

async function submitComment() {
  if (!(await ensureLogin('发表评论'))) return
  const content = newComment.value.trim()
  if (!content) {
    ElMessage.warning('内容不能为空')
    return
  }
  await commentApi.create({ blog: blogId.value, content })
  ElMessage.success('评论成功')
  newComment.value = ''
  await loadComments()
}

watch(blogId, () => {
  loadBlog()
  loadComments()
})

onMounted(() => {
  loadBlog()
  loadComments()
})
</script>

<template>
  <article v-if="blog" class="blog-detail">
    <h1 class="title">{{ blog.title }}</h1>
    <div class="meta">
      <img class="avatar" :src="blog.author?.avatar || '/default-avatar.svg'" />
      <span>{{ blog.author?.username }}</span>
      <span class="dot">·</span>
      <span>{{ blog.pub_time?.replace('T', ' ').slice(0, 16) }}</span>
      <el-tag v-if="blog.category" round size="small" class="category">{{ blog.category.name }}</el-tag>
    </div>

    <div class="blog-content" v-html="blog.content"></div>

    <div class="actions">
      <el-button :type="blog.is_liked ? 'primary' : 'default'" round @click="toggleLike">
        {{ blog.is_liked ? '💖 已赞' : '🤍 赞' }} {{ blog.total_likes }}
      </el-button>
      <el-button :type="blog.is_collected ? 'primary' : 'default'" round @click="toggleCollect">
        {{ blog.is_collected ? '⭐ 已收藏' : '☆ 收藏' }} {{ blog.total_collections }}
      </el-button>
    </div>

    <section class="comments">
      <h3>评论 ({{ comments.length }})</h3>
      <el-input v-model="newComment" type="textarea" :rows="3" placeholder="请输入评论..." />
      <div class="submit-wrap">
        <el-button type="primary" @click="submitComment">发表评论</el-button>
      </div>
      <CommentTree :comments="comments" :blog-id="blogId" @changed="loadComments" />
    </section>
  </article>

  <el-skeleton v-else :rows="6" animated />
</template>

<style scoped>
.title {
  margin-bottom: 16px;
}
.meta {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--font-color-sub);
  font-size: 0.9rem;
  border-bottom: 1px solid var(--soft-grey);
  padding-bottom: 16px;
}
.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--soft-grey);
  object-fit: cover;
}
.dot { margin: 0 4px; }
.category { margin-left: auto; }
.blog-content {
  margin: 24px 0;
  line-height: 1.8;
  font-size: 1rem;
  color: #1f2933;
}
.blog-content :deep(img) { max-width: 100%; }
.blog-content :deep(pre) {
  background: #0d1117;
  color: #f0f6fc;
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
}
.actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin: 32px 0;
}
.comments {
  margin-top: 24px;
  border-top: 1px solid var(--soft-grey);
  padding-top: 24px;
}
.submit-wrap {
  text-align: right;
  margin: 12px 0 24px;
}
</style>
