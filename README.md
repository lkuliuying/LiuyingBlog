# 🌟 流萤博客 (Liuying Blog)

前后端分离的个人博客系统：**Django + DRF** 提供 RESTful API，**Vue 3 + Vite + Element Plus** 构建 SPA。

## 🛠️ 技术栈

### 后端
- Python 3.13+
- Django 6.0
- Django REST Framework
- djangorestframework-simplejwt（JWT 认证）
- django-cors-headers / django-filter
- SQLite（默认）/ Redis（可选缓存）
- Jazzmin（Django Admin 主题）

### 前端
- Vue 3 + Vite + TypeScript
- Pinia（状态管理）+ Vue Router 4
- Element Plus（UI 组件库）
- axios（带 JWT 拦截 / 自动刷新 token）
- @wangeditor/editor-for-vue（富文本）
- highlight.js（详情页代码高亮）

## 📂 顶层目录

```text
F:\liuying/
├── liuyingblog/      # 项目配置（settings/urls/wsgi/asgi）
├── blog/             # 博客接口：分类、博客、评论、上传
├── liuyingauth/      # 认证接口：注册、登录、个人中心
├── frontend/         # Vue 3 SPA（独立 npm 项目）
├── media/            # 用户上传文件（头像、博客图片）
├── static/           # Django Admin / Jazzmin 静态资源
├── manage.py
└── requirements.txt
```

## 🔌 API 总览

所有业务接口统一以 `/api/` 开头：

| 路径 | 方法 | 说明 |
|---|---|---|
| `/api/auth/register/` | POST | 注册 |
| `/api/auth/login/` | POST | 登录 → access/refresh + user |
| `/api/auth/refresh/` | POST | 刷新 access token |
| `/api/auth/captcha/` | POST | 发送邮箱验证码 |
| `/api/auth/me/` | GET / PATCH | 当前用户信息 + 统计 / 修改用户名邮箱 |
| `/api/auth/me/password/` | POST | 修改密码 |
| `/api/auth/me/avatar/` | POST | 上传头像 |
| `/api/auth/me/blogs|comments|likes|collections/` | GET | 我的列表 |
| `/api/blogs/` | GET / POST | 博客列表 / 创建（搜索 `?search=`） |
| `/api/blogs/{id}/` | GET / PUT / DELETE | 博客详情 / 修改 / 删除 |
| `/api/blogs/{id}/like/` | POST | 切换点赞 |
| `/api/blogs/{id}/collect/` | POST | 切换收藏 |
| `/api/categories/` | GET | 分类列表 |
| `/api/comments/?blog=ID` | GET | 该博客的顶层评论树 |
| `/api/comments/` | POST | 发表评论（含 `parent` 回复） |
| `/api/comments/{id}/like/` | POST | 切换评论点赞 |
| `/api/uploads/editor/` | POST | wangEditor 图片/视频上传（需登录） |

写操作均需 `Authorization: Bearer <access_token>`，未登录走 `IsAuthenticatedOrReadOnly`。

## 🚀 本地启动

> 项目约定虚拟环境目录是 **`.venv/`**（不是 `venv/`），脚本与文档以此为准。

### 0. 一键启动（推荐）

仓库根目录已经放好启动脚本，会自动建 `.venv`、装 Python / npm 依赖、跑 migrate，最后并行起两个服务。如果 `.venv` 已经存在但还没装依赖，脚本也会补装。

```cmd
:: Windows（双击或在 cmd 里运行）
start.bat
```

```bash
# Linux / macOS / git-bash
./start.sh
```

启动后：
- 后端：http://127.0.0.1:8000
- 前端：http://localhost:5173 ← 开发请访问这个

首次跑会下载依赖，比较慢；之后再跑就是秒开。脚本会把本次服务进程记录在 `.run/` 下，启动失败时也会自动清理已经拉起的进程。

一键停止：

```cmd
:: Windows
stop.bat
```

```bash
# Linux / macOS / git-bash
./stop.sh
```

`start.bat` 会开两个新的 cmd 窗口；除了运行 `stop.bat`，也可以手动关闭这两个窗口。`start.sh` 是前台并行运行，也可以按 `Ctrl+C` 同时停止。

如需创建超级管理员，先 `start` 起服务，再开一个新终端：

```bash
.venv\Scripts\activate          # 或 source .venv/bin/activate
python manage.py createsuperuser
```

### 1. 手动启动后端

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux / macOS
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver     # http://127.0.0.1:8000
```

### 2. 手动启动前端

```bash
cd frontend
npm install
npm run dev                    # http://localhost:5173
```

`vite.config.ts` 已配 `/api` 与 `/media` 代理到 `127.0.0.1:8000`，开发期不需要额外 CORS 配置。

### 3. 生产构建

```bash
cd frontend && npm run build   # 生成 frontend/dist/
```

把 `dist/` 交给 Nginx，反向代理 `/api/`、`/media/`、`/admin/` 到 Django/Gunicorn。

## 🧪 后端验证（curl 速查）

```bash
# 注册（先调 /api/auth/captcha/ 拿到 4 位验证码）
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","email":"a@b.com","captcha":"1234","password":"123456"}'

# 登录
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"account":"alice","password":"123456"}'

# 携带 token 拿当前用户
curl http://127.0.0.1:8000/api/auth/me/ -H "Authorization: Bearer <ACCESS>"

# 列表
curl http://127.0.0.1:8000/api/blogs/?search=hello
```

## 🌐 生产环境 Nginx 示例

```nginx
server {
    listen 80;
    server_name www.liuying.com liuying.com;
    root /www/wwwroot/liuying/frontend/dist;
    index index.html;

    # 前端 SPA，命中不到的路径回落到 index.html
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API 反代到 Django
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # 媒体文件
    location ^~ /media/ {
        alias /www/wwwroot/liuying/media/;
        expires 30d;
    }

    # Django Admin 自身静态
    location ^~ /admin/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
    }

    location ^~ /static/ {
        alias /www/wwwroot/liuying/static/;
        expires 30d;
    }
}
```

## 📄 许可证

MIT License。

---

*重构时间：2026-06-20。*
