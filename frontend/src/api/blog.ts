import http from './http'
import type { AxiosProgressEvent } from 'axios'
import type {
  BlogCategory,
  BlogDetail,
  BlogListItem,
  Paginated,
} from '@/types'

export const blogApi = {
  list: (params?: { page?: number; search?: string }) =>
    http.get<Paginated<BlogListItem>>('/blogs/', { params }).then((r) => r.data),

  detail: (id: number | string) =>
    http.get<BlogDetail>(`/blogs/${id}/`).then((r) => r.data),

  create: (data: { title: string; content: string; category: number }) =>
    http.post<BlogDetail>('/blogs/', data).then((r) => r.data),

  toggleLike: (id: number | string) =>
    http.post<{ is_liked: boolean; total_likes: number }>(`/blogs/${id}/like/`)
      .then((r) => r.data),

  toggleCollect: (id: number | string) =>
    http.post<{ is_collected: boolean; total_collections: number }>(`/blogs/${id}/collect/`)
      .then((r) => r.data),

  categories: () =>
    http.get<BlogCategory[]>('/categories/').then((r) => r.data),

  uploadEditorImage: (file: File, onProgress?: (progress: number) => void) => {
    const data = new FormData()
    data.append('file', file)
    return http.post<{
      errno: number
      message?: string
      data: { url: string; alt: string; href: string }
    }>('/uploads/editor/', data, {
      onUploadProgress: (event: AxiosProgressEvent) => {
        if (!event.total || !onProgress) return
        onProgress(Math.min(99, Math.round((event.loaded / event.total) * 100)))
      },
    }).then((response) => {
      if (response.data.errno !== 0) {
        throw new Error(response.data.message || '图片上传失败')
      }
      return response.data.data
    })
  },
}
