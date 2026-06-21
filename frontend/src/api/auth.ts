import http from './http'
import type { LoginPayload, MeResponse, RegisterPayload, UserBrief } from '@/types'

export const authApi = {
  register: (data: RegisterPayload) =>
    http.post<UserBrief>('/auth/register/', data).then((r) => r.data),

  login: (data: LoginPayload) =>
    http.post<{ access: string; refresh: string; user: UserBrief }>('/auth/login/', data)
      .then((r) => r.data),

  refresh: (refresh: string) =>
    http.post<{ access: string }>('/auth/refresh/', { refresh }).then((r) => r.data),

  captcha: (email: string) =>
    http.post('/auth/captcha/', { email }).then((r) => r.data),

  me: () => http.get<MeResponse>('/auth/me/').then((r) => r.data),

  updateProfile: (data: { username?: string; email?: string }) =>
    http.patch<UserBrief>('/auth/me/', data).then((r) => r.data),

  changePassword: (data: { old_password: string; new_password1: string; new_password2: string }) =>
    http.post('/auth/me/password/', data).then((r) => r.data),

  uploadAvatar: (file: File) => {
    const fd = new FormData()
    fd.append('avatar', file)
    return http.post<{ avatar: string }>('/auth/me/avatar/', fd).then((r) => r.data)
  },

  myBlogs: () => http.get('/auth/me/blogs/').then((r) => r.data),
  myComments: () => http.get('/auth/me/comments/').then((r) => r.data),
  myLikes: () => http.get('/auth/me/likes/').then((r) => r.data),
  myCollections: () => http.get('/auth/me/collections/').then((r) => r.data),
}
