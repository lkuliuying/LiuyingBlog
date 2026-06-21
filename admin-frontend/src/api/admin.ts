import type { AxiosProgressEvent } from 'axios'

import http from './http'
import type {
  AdminBlog,
  AdminComment,
  AdminIdentity,
  AdminUser,
  Category,
  DashboardData,
  Paginated,
} from '@/types'

export interface ListParams {
  page?: number
  page_size?: number
  search?: string
  category?: number | string
  author?: number | string
  blog?: number | string
  role?: string
  active?: string
  ordering?: string
  date_from?: string
  date_to?: string
}

export const adminApi = {
  async login(payload: { account: string; password: string }) {
    const { data } = await http.post<{
      access: string
      refresh: string
      user: AdminIdentity
    }>('/admin/auth/login/', payload)
    return data
  },
  async refresh(refresh: string) {
    const { data } = await http.post<{ access: string }>('/admin/auth/refresh/', { refresh })
    return data
  },
  async me() {
    const { data } = await http.get<AdminIdentity>('/admin/auth/me/')
    return data
  },
  async dashboard() {
    const { data } = await http.get<DashboardData>('/admin/dashboard/')
    return data
  },
  async blogs(params: ListParams) {
    const { data } = await http.get<Paginated<AdminBlog>>('/admin/blogs/', { params })
    return data
  },
  async blog(id: number) {
    const { data } = await http.get<AdminBlog>(`/admin/blogs/${id}/`)
    return data
  },
  async saveBlog(payload: {
    id?: number
    title: string
    content: string
    category_id: number
  }) {
    if (payload.id) {
      const { data } = await http.patch<AdminBlog>(`/admin/blogs/${payload.id}/`, payload)
      return data
    }
    const { data } = await http.post<AdminBlog>('/admin/blogs/', payload)
    return data
  },
  deleteBlog(id: number) {
    return http.delete(`/admin/blogs/${id}/`)
  },
  bulkDeleteBlogs(ids: number[]) {
    return http.post('/admin/blogs/bulk-delete/', { ids })
  },
  async categories() {
    const { data } = await http.get<Category[]>('/admin/categories/')
    return data
  },
  async saveCategory(payload: { id?: number; name: string }) {
    if (payload.id) {
      const { data } = await http.patch<Category>(`/admin/categories/${payload.id}/`, payload)
      return data
    }
    const { data } = await http.post<Category>('/admin/categories/', payload)
    return data
  },
  deleteCategory(id: number) {
    return http.delete(`/admin/categories/${id}/`)
  },
  async comments(params: ListParams) {
    const { data } = await http.get<Paginated<AdminComment>>('/admin/comments/', { params })
    return data
  },
  deleteComment(id: number) {
    return http.delete(`/admin/comments/${id}/`)
  },
  bulkDeleteComments(ids: number[]) {
    return http.post('/admin/comments/bulk-delete/', { ids })
  },
  async users(params: ListParams) {
    const { data } = await http.get<Paginated<AdminUser>>('/admin/users/', { params })
    return data
  },
  async user(id: number) {
    const { data } = await http.get<AdminUser>(`/admin/users/${id}/`)
    return data
  },
  async updateUser(id: number, payload: Partial<Pick<AdminUser, 'username' | 'email' | 'is_active' | 'is_staff'>>) {
    const { data } = await http.patch<AdminUser>(`/admin/users/${id}/`, payload)
    return data
  },
  deleteUser(id: number) {
    return http.delete(`/admin/users/${id}/`)
  },
  async uploadImage(file: File, onProgress?: (percent: number) => void) {
    const form = new FormData()
    form.append('file', file)
    const { data } = await http.post<{
      errno: number
      data: { url: string; alt: string; href: string }
    }>('/uploads/editor/', form, {
      onUploadProgress(event: AxiosProgressEvent) {
        if (event.total) onProgress?.(Math.round((event.loaded / event.total) * 100))
      },
    })
    return data.data
  },
}

