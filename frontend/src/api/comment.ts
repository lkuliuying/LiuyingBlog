import http from './http'
import type { Comment } from '@/types'

export const commentApi = {
  listByBlog: (blogId: number | string) =>
    http.get<Comment[]>('/comments/', { params: { blog: blogId } }).then((r) => r.data),

  create: (data: { blog: number | string; content: string; parent?: number | null }) =>
    http.post<Comment>('/comments/', data).then((r) => r.data),

  toggleLike: (id: number) =>
    http.post<{ is_liked: boolean; total_likes: number }>(`/comments/${id}/like/`)
      .then((r) => r.data),
}
