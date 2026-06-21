<script setup lang="ts">
import CommentItem from './CommentItem.vue'
import type { Comment } from '@/types'

defineProps<{ comments: Comment[]; blogId: number | string }>()
const emit = defineEmits<{ (e: 'changed'): void }>()
</script>

<template>
  <div class="comment-tree">
    <p v-if="!comments.length" class="empty">还没有评论，来抢沙发吧～</p>
    <CommentItem
      v-for="c in comments"
      :key="c.id"
      :comment="c"
      :blog-id="blogId"
      @replied="emit('changed')"
    />
  </div>
</template>

<style scoped>
.empty {
  color: var(--font-color-sub);
  text-align: center;
  padding: 24px 0;
}
</style>
