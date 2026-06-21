<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

import { commentApi } from '@/api/comment'
import type { Comment } from '@/types'
import { useAuthStore } from '@/stores/auth'

const props = defineProps<{ comment: Comment; blogId: number | string }>()
const emit = defineEmits<{ (e: 'replied'): void }>()

const auth = useAuthStore()
const showReply = ref(false)
const replyContent = ref('')
const liked = ref(props.comment.is_liked)
const likeCount = ref(props.comment.total_likes)

async function toggleLike() {
  if (!auth.isLogin) {
    ElMessage.warning('请先登录后再点赞评论')
    return
  }
  const data = await commentApi.toggleLike(props.comment.id)
  liked.value = data.is_liked
  likeCount.value = data.total_likes
}

async function submitReply() {
  if (!auth.isLogin) {
    ElMessage.warning('请先登录后再回复')
    return
  }
  const content = replyContent.value.trim()
  if (!content) {
    ElMessage.warning('内容不能为空')
    return
  }
  await commentApi.create({
    blog: props.blogId,
    content,
    parent: props.comment.id,
  })
  ElMessage.success('回复成功')
  replyContent.value = ''
  showReply.value = false
  emit('replied')
}
</script>

<template>
  <div class="comment-node">
    <div class="head">
      <img class="avatar" :src="comment.author?.avatar || '/default-avatar.svg'" />
      <div class="meta">
        <strong>{{ comment.author?.username }}</strong>
        <span class="time">{{ comment.pub_time?.replace('T', ' ').slice(0, 16) }}</span>
      </div>
    </div>
    <div class="body">{{ comment.content }}</div>
    <div class="actions">
      <button class="like-btn" :class="{ active: liked }" @click="toggleLike">
        <span>{{ liked ? '💖' : '🤍' }}</span>
        <span>{{ likeCount }}</span>
      </button>
      <el-button link type="primary" size="small" @click="showReply = !showReply">
        {{ showReply ? '取消' : '回复' }}
      </el-button>
    </div>

    <div v-if="showReply" class="reply-form">
      <el-input v-model="replyContent" type="textarea" :rows="2" :placeholder="`回复 @${comment.author?.username}`" />
      <div class="reply-submit">
        <el-button size="small" type="primary" @click="submitReply">发送</el-button>
      </div>
    </div>

    <div v-if="comment.replies?.length" class="children">
      <CommentItem
        v-for="child in comment.replies"
        :key="child.id"
        :comment="child"
        :blog-id="blogId"
        @replied="emit('replied')"
      />
    </div>
  </div>
</template>

<script lang="ts">
// 递归引用自己时需要给组件命名
export default { name: 'CommentItem' }
</script>

<style scoped>
.comment-node {
  border-top: 1px solid var(--soft-grey);
  padding: 14px 0;
}
.head {
  display: flex;
  align-items: center;
  gap: 10px;
}
.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
  background: var(--soft-grey);
}
.meta strong {
  font-size: 0.92rem;
}
.time {
  margin-left: 8px;
  font-size: 0.8rem;
  color: var(--font-color-sub);
}
.body {
  margin: 8px 0 8px 42px;
  white-space: pre-wrap;
  line-height: 1.6;
}
.actions {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-left: 42px;
}
.like-btn {
  background: none;
  border: 0;
  cursor: pointer;
  font-size: 0.85rem;
  color: var(--font-color-sub);
  padding: 4px 6px;
  border-radius: 4px;
}
.like-btn.active {
  color: var(--primary-mint);
}
.reply-form {
  margin: 8px 0 4px 42px;
}
.reply-submit {
  margin-top: 8px;
  text-align: right;
}
.children {
  margin-left: 42px;
  border-left: 2px solid var(--soft-grey);
  padding-left: 16px;
}
</style>
