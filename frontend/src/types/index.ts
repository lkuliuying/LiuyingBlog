// 共享的接口数据类型

export interface UserBrief {
  id: number
  username: string
  email: string
  avatar: string
}

export interface BlogCategory {
  id: number
  name: string
}

export interface BlogAuthor {
  id: number
  username: string
  avatar: string
}

export interface BlogListItem {
  id: number
  title: string
  summary: string
  first_image: string | null
  author: BlogAuthor
  category: BlogCategory | null
  pub_time: string
  total_likes: number
  total_collections: number
}

export interface BlogDetail {
  id: number
  title: string
  content: string
  pub_time: string
  updated_time: string
  author: BlogAuthor
  category: BlogCategory | null
  total_likes: number
  total_collections: number
  is_liked: boolean
  is_collected: boolean
}

export interface Comment {
  id: number
  blog: number
  content: string
  pub_time: string
  parent: number | null
  author: BlogAuthor
  replies: Comment[]
  total_likes: number
  is_liked: boolean
}

export interface Paginated<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface RegisterPayload {
  username: string
  email: string
  captcha: string
  password: string
}

export interface LoginPayload {
  account: string
  password: string
}

export interface MeStats {
  blogs: number
  comments: number
  likes: number
  collections: number
}

export interface MeResponse {
  user: UserBrief
  stats: MeStats
}
