export interface AdminIdentity {
  id: number
  username: string
  email: string
  avatar: string
  is_staff: boolean
  is_superuser: boolean
}

export interface Category {
  id: number
  name: string
  blog_count: number
}

export interface AdminBlog {
  id: number
  title: string
  content: string
  summary: string
  author: AdminIdentity
  category: Category
  pub_time: string
  updated_time: string
  total_likes: number
  total_collections: number
}

export interface AdminComment {
  id: number
  blog: number
  blog_title: string
  author: AdminIdentity
  content: string
  parent: number | null
  parent_content?: string
  pub_time: string
  total_likes: number
}

export interface AdminUser extends AdminIdentity {
  is_active: boolean
  date_joined: string
  last_login: string | null
  blog_count: number
  comment_count: number
  follower_count: number
  following_count: number
}

export interface Paginated<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface DashboardData {
  totals: {
    users: number
    blogs: number
    comments: number
    categories: number
  }
  today: {
    users: number
    blogs: number
    comments: number
  }
  trend: Array<{
    date: string
    users: number
    blogs: number
    comments: number
  }>
  recent_blogs: AdminBlog[]
  recent_comments: AdminComment[]
}

