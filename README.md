# 🌟 流萤博客 (Liuying Blog)

前后端分离的个人博客系统：**Django + DRF** 提供 RESTful API，**Vue 3 + Vite + Element Plus** 构建两套独立 SPA —— 一套面向读者/作者的前台，一套面向运营的管理后台。


## 🛠️ 技术栈

### 后端
- Python 3.13+
- Django 6.0（仅作为 ORM / Auth / Middleware 基座；admin / staticfiles / sessions / messages 均已禁用）
- Django REST Framework
- djangorestframework-simplejwt（JWT 认证）
- django-cors-headers / django-filter
- SQLite（默认）/ Redis（缓存）

### 前端（两个独立项目）
- Vue 3 + Vite + TypeScript
- Pinia（状态管理）+ Vue Router 4
- Element Plus（UI 组件库）
- axios（带 JWT 拦截 / 自动刷新 token）
- @wangeditor/editor-for-vue（富文本）
- highlight.js（详情页代码高亮）

## 📂 顶层目录

```text
项目根目录/
├── liuyingblog/      # 项目配置（settings/urls/wsgi/asgi）
├── blog/             # 前台博客接口：分类、博客、评论、上传
├── liuyingauth/      # 认证接口：注册、登录、个人中心
├── adminapi/         # 管理后台接口：博客/分类/评论/用户 CRUD + Dashboard
├── frontend/         # 用户前台 SPA（独立 npm 项目，端口 5173）
├── admin-frontend/   # 管理后台 SPA（独立 npm 项目，端口 5174，挂在 /manage/）
├── media/            # 用户上传文件（头像、博客图片）
├── start-user.bat    # Windows：后端 + 用户前台
├── start-admin.bat   # Windows：后端 + 管理后台
├── start-stack.ps1   # Windows 共用启动逻辑（自动复用已运行的后端）
├── start.bat         # 兼容入口：后端 + 用户前台
├── start.sh          # Linux/macOS：后端 + 用户前台
├── stop.bat/.sh      # 停止由脚本启动的服务
├── manage.py
└── requirements.txt
```

`media/`、SQLite 数据库、`.env`、虚拟环境和前端构建产物均为本地运行数据，已通过 `.gitignore` 排除。

## 🔌 API 总览

所有业务接口统一以 `/api/` 开头，按受众划分为三组：

### 认证 `/api/auth/`

| 路径 | 方法 | 说明 |
|---|---|---|
| `/api/auth/register/` | POST | 注册（需先调 `captcha/` 拿 4 位邮箱验证码） |
| `/api/auth/login/` | POST | 登录 → `access` / `refresh` + `user` |
| `/api/auth/refresh/` | POST | 刷新 access token |
| `/api/auth/captcha/` | POST | 发送邮箱验证码 |
| `/api/auth/me/` | GET / PATCH | 当前用户信息 + 统计 / 修改用户名邮箱 |
| `/api/auth/me/password/` | POST | 修改密码 |
| `/api/auth/me/avatar/` | POST | 上传头像 |
| `/api/auth/me/blogs\|comments\|likes\|collections/` | GET | 我的列表 |

### 前台博客 `/api/`

| 路径 | 方法 | 说明 |
|---|---|---|
| `/api/blogs/` | GET / POST | 博客列表 / 创建（搜索 `?search=`） |
| `/api/blogs/{id}/` | GET / PUT / DELETE | 博客详情 / 修改 / 删除 |
| `/api/blogs/{id}/like/` | POST | 切换点赞 |
| `/api/blogs/{id}/collect/` | POST | 切换收藏 |
| `/api/categories/` | GET | 分类列表 |
| `/api/comments/?blog=ID` | GET | 该博客的顶层评论树 |
| `/api/comments/` | POST | 发表评论（含 `parent` 回复） |
| `/api/comments/{id}/like/` | POST | 切换评论点赞 |
| `/api/uploads/editor/` | POST | wangEditor 图片/视频上传（需登录） |

### 管理后台 `/api/admin/`

仅放行 `is_staff=True` 的用户；登录独立维护一套 JWT，与前台用户登录互不影响。

| 路径 | 方法 | 说明 |
|---|---|---|
| `/api/admin/auth/login/` | POST | 管理员登录 |
| `/api/admin/auth/refresh/` | POST | 刷新 token |
| `/api/admin/auth/me/` | GET | 当前管理员身份 |
| `/api/admin/dashboard/` | GET | 概览统计：用户/博客/评论计数、近 7 日趋势 |
| `/api/admin/blogs/` | GET / POST / PUT / DELETE | 博客 CRUD（含批量操作） |
| `/api/admin/categories/` | GET / POST / PUT / DELETE | 分类管理 |
| `/api/admin/comments/` | GET / DELETE | 评论审核与删除 |
| `/api/admin/users/` | GET / PATCH | 用户管理（启停、改角色） |

前台写操作走 `IsAuthenticatedOrReadOnly`；管理后台所有接口走 `IsAdminUser`。

> ❌ `path('admin/', admin.site.urls)` 已从根路由删除，访问 `/admin/` 会 404。如需新建管理员账号，直接用 `python manage.py createsuperuser` 后登录 `/manage/`（admin-frontend）。

## 🚀 本地启动

> 项目约定虚拟环境目录是 **`.venv/`**（不是 `venv/`），脚本与文档以此为准。

### 0. 配置环境变量

首次启动前可复制示例配置：

```powershell
Copy-Item .env.example .env
```

```bash
cp .env.example .env
```

至少应在生产环境中设置安全的 `DJANGO_SECRET_KEY`、关闭 `DJANGO_DEBUG`，并填写邮件和 Redis 配置。`.env` 不应提交到 Git。

### 1. Windows 一键启动（推荐）

脚本会自动创建 `.venv`、安装或更新 Python/npm 依赖、执行数据库迁移，并启动所选前端。后端已经健康运行时会直接复用，不会重复占用 8000 端口。

```cmd
:: 用户前台 + Django 后端
start-user.bat

:: 管理后台 + Django 后端
start-admin.bat
```

兼容旧用法的 `start.bat` 仍会启动 Django 后端和用户前台，但不会复用已占用的端口；日常开发优先使用上面的两个入口。

启动后：

- 后端：http://127.0.0.1:8000
- 用户前台：http://localhost:5173
- 管理后台：http://localhost:5174/manage/

需要同时开发两套前端时，先运行 `start-user.bat`，再运行 `start-admin.bat`；第二个脚本会复用已经启动的 Django 后端。

一键停止：

```cmd
stop.bat
```

### 2. Linux / macOS 一键启动

```bash
./start.sh
```

该脚本启动 Django 后端和用户前台。管理后台可按下文的手动方式另行启动。

一键停止：

```bash
./stop.sh
```

首次运行会下载依赖，耗时相对较长；后续启动会明显更快。脚本将服务 PID 记录在 `.run/`，该目录不会提交到 Git。

如需创建管理员账号，先 `start` 起服务，再开一个新终端：

```bash
.venv\Scripts\activate          # 或 source .venv/bin/activate
python manage.py createsuperuser
```

> 创建出来的超级用户默认 `is_staff=True`，可直接登录 `/manage/`。也可以建一个普通用户后用 `python manage.py shell` 把它的 `is_staff` 改成 `True`，作为运营账号。

### 3. 手动启动后端

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux / macOS
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver      # http://127.0.0.1:8000
```

### 4. 手动启动用户前台 `frontend/`

```bash
cd frontend
npm install
npm run dev                     # http://localhost:5173
```

`frontend/vite.config.ts` 已配 `/api` 与 `/media` 代理到 `127.0.0.1:8000`，开发期不需要额外 CORS 配置。

### 5. 手动启动管理后台 `admin-frontend/`

```bash
cd admin-frontend
npm install
npm run dev                     # http://localhost:5174/manage/
```

管理后台跑在 **5174 端口**，路径前缀 `/manage/`（由 `vite.config.ts` 的 `base` 决定，与生产部署路径对齐）。同样代理 `/api` 与 `/media` 到 `127.0.0.1:8000`。

首次进入需用 `is_staff=True` 的账号登录，否则 `/api/admin/auth/login/` 会返回 403。

### 6. 生产构建

```bash
cd frontend       && npm run build      # → frontend/dist/        部署到 /
cd admin-frontend && npm run build      # → admin-frontend/dist/  部署到 /manage/
```

把两个 `dist/` 分别交给 Nginx，反向代理 `/api/`、`/media/` 到 Django/Gunicorn（见下方示例）。后端**不需要 collectstatic**——Django Admin 已移除，没有自身静态资源要服务。

## 🧪 后端验证（curl 速查）

```bash
# 注册（先调 /api/auth/captcha/ 拿到 4 位验证码）
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","email":"a@b.com","captcha":"1234","password":"123456"}'

# 用户登录
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"account":"alice","password":"123456"}'

# 携带 token 拿当前用户
curl http://127.0.0.1:8000/api/auth/me/ -H "Authorization: Bearer <ACCESS>"

# 列表
curl http://127.0.0.1:8000/api/blogs/?search=hello

# 管理员登录
curl -X POST http://127.0.0.1:8000/api/admin/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Dashboard 概览
curl http://127.0.0.1:8000/api/admin/dashboard/ -H "Authorization: Bearer <ADMIN_ACCESS>"
```

## 🌐 生产环境 Nginx 示例

```nginx
server {
    listen 80;
    server_name www.liuying.com liuying.com;
    index index.html;

    # 用户前台 SPA（根路径）
    location / {
        root /www/wwwroot/liuying/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # 管理后台 SPA（/manage/）
    location /manage/ {
        alias /www/wwwroot/liuying/admin-frontend/dist/;
        try_files $uri $uri/ /manage/index.html;
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
}
```

> 旧版本 Nginx 配置里的 `/admin/` 反代和 `/static/` alias 都可以删掉了：前者已 404，后者 Django 不再产出。

## 📄 许可证

MIT License。

---

*最后更新：2026-06-21（同步 Windows 双前端启动方式、环境变量说明与仓库忽略规则）。*
