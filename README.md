# 🌟 流萤博客 (Liuying Blog)

一个基于 Django 6.0 构建的生产级个人博客系统。本项目采用**务实的混合架构**，既保证了传统模板渲染的 SEO 优势，又预留了完整的 RESTful API 扩展能力。所有功能均经过云服务器生产环境验证，代码简洁实用，无过度设计。

## 🛠️ 技术栈

### 后端核心
- **Python**: 3.13+
- **Web 框架**: Django 6.0.3
- **API 框架**: Django REST Framework (DRF) - 支持分页与标准化接口
- **数据库**: SQLite 3 (读多写少场景的最优解)
- **缓存层**: Redis (Session 存储 + 数据缓存，已配置但未强制依赖)
- **异步任务**: Celery (邮件异步发送，使用Redis作为消息代理)
- **邮件服务**: SMTP (QQ邮箱集成，用于验证码发送)

### 前端技术
- **UI 框架**: Bootstrap 5 (响应式设计)
- **富文本编辑器**: WangEditor V5 (支持图片/视频上传)
- **JavaScript**: 原生 Fetch API + jQuery (AJAX 交互)
- **CSS 高亮**: Highlight.js (代码语法高亮)

### 部署环境
- **操作系统**: CentOS 9 / Windows (开发环境)
- **Web 服务器**: Nginx (反向代理 + 静态资源托管)
- **WSGI 服务器**: Gunicorn (生产环境) / Django runserver (开发环境)
- **进程管理**: Systemd (生产环境守护)
- **控制面板**: 宝塔面板 (可选)

## ✨ 核心功能

### 👤 用户认证系统
- **灵活登录方式**: 支持用户名或邮箱登录（自定义认证后端 `EmailOrUsernameModelBackend`）
- **邮箱注册验证**: 4位数字验证码，60秒防刷限流保护
- **无刷新头像上传**: 悬浮遮罩触发，即时预览并处理浏览器缓存
- **个人信息管理**: 
  - 用户名/邮箱异步修改（Fetch API），页面顶部实时同步
  - 密码安全重置（`update_session_auth_hash` 保持登录态）
- **社交互动**:
  - 关注/粉丝系统（单向关注关系）
  - 个人中心聚合展示：发布的博客、历史评论、点赞文章、收藏文章

### ✍️ 博客内容系统
- **WangEditor V5 深度集成**: 
  - 支持富文本编辑（加粗、斜体、列表、表格等）
  - 图片/视频上传（限制 10MB，白名单格式校验）
  - 按年/月自动分类存储，UUID 重命名防冲突
- **智能封面提取**: 后端 `@property` 方法使用正则从 HTML 中提取首图作为卡片封面
- **分类管理**: 多级博客分类，后台可配置
- **全文搜索**: 支持标题和内容的模糊搜索（Q对象 OR 查询）
- **SEO 友好**: 传统模板渲染，搜索引擎可直接抓取内容

### 💬 评论与互动系统
- **嵌套评论**: 支持回复特定评论（父子评论结构）
- **点赞功能**: 
  - 博客文章点赞/取消点赞（ManyToManyField 实现）
  - 评论点赞/取消点赞
- **收藏功能**: 博客文章收藏/取消收藏
- **实时反馈**: AJAX 异步操作，无需刷新页面即可看到状态变化

### 🛡️ 后台管理系统
- **Jazzmin 主题**: Bootstrap 4 现代化响应式 UI，替代默认 Admin 界面
- **深度定制**:
  - 博客列表：显示 ID、标题、作者、分类、发布时间，支持过滤和搜索
  - 评论列表：截断显示评论内容（最多 50 字符），关联博客信息
  - 分类管理：简洁的分类增删改查
- **数据可视化**: 左上角显示"流萤博客管理后台"品牌标识

### 🔌 RESTful API 接口
- **标准化接口**: DRF 序列化器将模型转换为 JSON 格式
- **分页支持**: PageNumberPagination，每页默认 10 条数据
- **接口示例**:
  - `GET /api/blogs/` - 获取博客列表（带分页）
  - 返回字段：id, title, content, pub_time, author_name
- **可扩展性**: 未来可轻松接入微信小程序、移动端 App 或 AI 应用

### 📊 日志管理系统
- **分级记录**: INFO、WARNING、ERROR 三级日志分层存储
- **按日期和类型分类**: 日志文件按类型（error.log、info.log）存储，备份文件按日期命名（如 error.log.2026-04-26）
- **自动轮换**: 每天午夜自动轮换，保留 30 天历史日志
- **高效存储**: 单个日志文件最大 10MB，超出后自动分割

## 📂 项目目录结构

```text
F:\liuying/
├── liuyingblog/            # 项目全局配置
│   ├── settings.py         # 核心配置 (DEBUG, ALLOWED_HOSTS, DRF, Redis, Email等)
│   ├── urls.py             # 主路由分发 (admin, blog, auth)
│   ├── wsgi.py             # WSGI 入口
│   └── asgi.py             # ASGI 入口
│
├── blog/                   # 核心业务应用
│   ├── models.py           # 数据模型 (Blog, BlogCategory, BlogComment)
│   │                       #   - first_image 属性：正则提取首图
│   │                       #   - likes/collections: ManyToManyField
│   ├── views.py            # 视图层 (网页渲染、文件上传、点赞/收藏)
│   ├── api_views.py        # DRF 接口视图 (API数据分发)
│   ├── serializers.py      # DRF 序列化器 (BlogSerializer)
│   ├── forms.py            # 表单验证 (PubBlogForm)
│   ├── admin.py            # 后台管理深度定制 (Jazzmin集成)
│   ├── urls.py             # 业务路由 (12个URL端点)
│   ├── templatetags/       # 自定义模板标签 (comment_tags)
│   └── migrations/         # 数据库迁移文件
│
├── liuyingauth/            # 用户认证应用
│   ├── models.py           # 用户模型 (CaptchaModel, UserProfile)
│   ├── views.py            # 登录/注册/个人中心/头像上传/信息修改
│   ├── backends.py         # 自定义认证后端 (邮箱/用户名登录)
│   ├── forms.py            # 表单验证 (LoginForm, RegisterForm)
│   ├── urls.py             # 认证路由 (8个URL端点)
│   └── migrations/         # 数据库迁移文件
│
├── templates/              # HTML 模板
│   ├── base.html           # 基础模板 (导航栏 + Footer)
│   ├── index.html          # 首页 (博客列表)
│   ├── blog_detail.html    # 博客详情页 (含评论区)
│   ├── pub_blog.html       # 发布博客页 (WangEditor集成)
│   ├── login.html          # 登录页
│   ├── register.html       # 注册页
│   ├── user_profile.html   # 个人中心 (头像/信息/密码/博客/评论)
│   └── comments/           # 评论组件模板
│       └── comment_tree.html
│
├── static/                 # 静态资源 (由 collectstatic 收集)
│   ├── bootstrap5/         # Bootstrap 5 CSS/JS
│   ├── wangeditor/         # 富文本编辑器 JS/CSS
│   ├── highlight/          # 代码高亮库
│   ├── jquery/             # jQuery 3.7.1
│   ├── css/                # 自定义样式
│   ├── js/                 # 自定义脚本 (pub_blog.js, register.js)
│   └── image/              # 静态图片 (logo, 默认头像)
│
├── media/                  # 用户上传文件 (Nginx 直接托管)
│   ├── avatars/YYYY/MM/    # 用户头像 (按年月分类)
│   └── upload/YYYY/MM/     # 博客图片/视频 (按年月分类)
│
├── logs/                   # 日志文件 (按类型和日期分类)
│   ├── error.log           # 错误日志 (WARNING+)
│   ├── info.log            # 信息日志 (INFO+)
│   └── *.log.YYYY-MM-DD    # 历史日志备份
│
├── .env                    # 环境变量 (SECRET_KEY, DEBUG, EMAIL_PASSWORD)
├── requirements.txt        # Python 依赖包
├── manage.py               # Django 管理脚本
├── start.bat               # 一键启动脚本 (Windows)
├── stop.bat                # 一键停止脚本 (Windows)
├── db.sqlite3              # SQLite 数据库文件
├── .gitignore              # Git 忽略文件
└── README.md               # 项目文档
```

## 🏗️ 架构设计理念

### 1. 务实的混合架构
拒绝为了炫技而盲目进行“前后端分离”。主站采用 Django Template 渲染，保证了极佳的 SEO 和首屏加载速度（对博客至关重要）；同时通过 DRF 平行构建了一套 RESTful API，未来无论是接入微信小程序还是大模型 AI，都不需要重构底层。

### 2. 克制的数据库选型
基于博客“读多写少”的业务模型，坚持使用 SQLite，避免了引入额外中间件（如 MySQL/Redis）的运维成本，单文件备份极其方便。同时配置了 Redis 缓存层（可选），用于 Session 存储和数据缓存，提升高并发性能。

### 3. 防御性的 Nginx 配置
针对宝塔面板默认反向代理 `location ^~ /` 导致的“静态文件拦截死锁”问题，精准使用 `location ^~ /static/` 和 `location ^~ /media/` 提升优先级，实现了静态资源由 Nginx 高效托管，动态请求由 Django 处理的完美解耦。

### 4. 安全性设计
- **环境变量管理**: `.env` 文件隔离敏感信息（SECRET_KEY、邮箱密码）
- **CSRF 保护**: 所有 POST 请求默认启用 CSRF 校验（富文本上传特殊处理）
- **登录验证**: `@login_required` 装饰器保护敏感接口
- **防刷限流**: 邮箱验证码 60 秒冷却时间
- **文件上传安全**: 白名单格式校验 + 10MB 大小限制 + UUID 重命名

## 🚀 本地快速运行

### 前置要求
- Python 3.13+
- pip (Python 包管理器)
- Git (可选，用于克隆项目)
- Redis (可选，用于缓存和异步任务)

### 安装步骤

```bash
# 1. 克隆项目
git clone <your-repo-url>
cd liuying

# 2. 创建并激活虚拟环境
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
# 复制环境变量示例文件
copy .env.example .env
# 编辑 .env 文件，设置 SECRET_KEY 和其他敏感信息

# 5. 执行数据库迁移
python manage.py migrate

# 6. 创建超级管理员
python manage.py createsuperuser

# 7. 收集静态文件（生产环境必需）
python manage.py collectstatic --noinput

# 8. 一键启动服务 (Windows)
# 启动 Redis, Celery 和 Django
.\start.bat

# 或者手动启动
# 启动 Redis (如果使用)
# redis-server
# 启动 Celery
# celery -A liuyingblog worker --loglevel=info --pool=solo
# 启动 Django
# python manage.py runserver
```

### 访问地址
- **首页**: http://127.0.0.1:8000/
- **后台管理**: http://127.0.0.1:8000/admin/
- **API 接口**: http://127.0.0.1:8000/api/blogs/
- **用户注册**: http://127.0.0.1:8000/auth/register
- **用户登录**: http://127.0.0.1:8000/auth/login

### 停止服务
```bash
# Windows 一键停止
.\stop.bat

# 或手动停止
# 停止 Django (Ctrl+C)
# 停止 Celery (Ctrl+C in Celery window)
# 停止 Redis (Ctrl+C in Redis window)
```

## 💡 踩坑记录

本项目非教程照搬，所有坑均在实战中解决：

### Python & Django 相关
- **Python 3.13 兼容性**: Django 6.0 严格校验 MySQL 驱动版本，使用 PyMySQL 必须在 `__init__.py` 中伪装版本号才能绕过校验（本项目已切换至 SQLite，无需此操作）
- **生产环境 DEBUG=False 的连环坑**:
  - 关闭 Debug 不仅引发 400 错误，还会导致 Django 拒绝服务静态/媒体文件
  - 必须配合 `collectstatic` 和严谨的 Nginx `alias` 规则
  - ALLOWED_HOSTS 必须正确配置域名和 IP

### WangEditor V5 集成
- **配置项名极其严格**: `MENU_CONF` 拼写错误会导致静默失败
- **上传限制**: 默认 2MB 上传限制需手动通过 `maxFileSize` 解除（本项目设置为 10MB）
- **CSRF 豁免**: 富文本编辑器文件上传接口需要使用 `@csrf_exempt`（已通过 `@login_required` 保证安全）

### 前端缓存问题
- **浏览器缓存坑**: 修改外部引用的 JS 文件后，必须通过更改 `<script src="...?v=x">` 的版本号来强制客户端更新，否则极易产生“代码没生效”的错觉
- **头像缓存**: 上传新头像后，URL 不变会导致浏览器显示旧图，需在 URL 后添加时间戳参数

### 本地访问报错排查
如果访问 `http://127.0.0.1:8000/` 出现"URL拼写可能存在错误，请检查"的提示，请确认：
1. Django开发服务器是否正常启动（查看终端输出）
2. 项目主路由 `liuyingblog/urls.py` 中是否正确配置了首页路由
3. 浏览器是否有缓存问题，尝试强制刷新（Ctrl+F5）
4. 数据库迁移是否完成（`python manage.py migrate`）
5. 是否有未捕获的 Python 异常（查看终端错误日志）

### 邮箱验证码发送失败
- 检查 `.env` 文件中 `EMAIL_HOST_PASSWORD` 是否配置正确（QQ邮箱需使用授权码，而非登录密码）
- 确认 QQ 邮箱已开启 SMTP 服务
- 检查防火墙是否阻止 587 端口

### 日志文件权限问题
- Windows 下日志文件被占用时，TimedRotatingFileHandler 可能报 PermissionError
- 已优化为 RotatingFileHandler，按文件大小轮换，避免时间轮换的锁定问题

## 📊 API 接口文档

### 博客列表 API
**请求**: `GET /api/blogs/?page=1`

**响应示例**:
```json
{
  "count": 100,
  "next": "http://127.0.0.1:8000/api/blogs/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "我的第一篇博客",
      "content": "<p>博客内容...</p>",
      "pub_time": "2026-04-17T10:00:00",
      "author_name": "admin"
    }
  ]
}
```

### 点赞/收藏/评论互动 API
- **博客点赞**: `POST /blog/<blog_id>/like/` (需登录)
- **博客收藏**: `POST /blog/<blog_id>/collect/` (需登录)
- **评论点赞**: `POST /comment/<comment_id>/like/` (需登录)

**响应示例**:
```json
{
  "status": "success",
  "is_liked": true,
  "total_likes": 42
}
```

### 用户信息 API
- **上传头像**: `POST /auth/upload_avatar/` (需登录, multipart/form-data)
- **修改信息**: `POST /auth/profile/update_info/` (需登录)
- **修改密码**: `POST /auth/profile/update_password/` (需登录)
- **获取验证码**: `GET /auth/captcha?email=xxx@qq.com`

## 🔧 生产环境部署

### Nginx 配置示例
```nginx
server {
    listen 80;
    server_name www.liuying.com liuying.com;

    # 静态文件
    location ^~ /static/ {
        alias /www/wwwroot/liuying/static/;
        expires 30d;
    }

    # 媒体文件
    location ^~ /media/ {
        alias /www/wwwroot/liuying/media/;
        expires 30d;
    }

    # 动态请求
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### Gunicorn 启动命令
```bash
gunicorn --workers 3 --bind 127.0.0.1:8000 liuyingblog.wsgi:application
```

### Systemd 服务配置
创建 `/etc/systemd/system/liuying.service`:
```ini
[Unit]
Description=Liuying Blog Gunicorn Service
After=network.target

[Service]
User=www
Group=www
WorkingDirectory=/www/wwwroot/liuying
ExecStart=/www/wwwroot/liuying/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 liuyingblog.wsgi:application
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

启用服务:
```bash
sudo systemctl enable liuying
sudo systemctl start liuying
```

## 📄 许可证

本项目采用 MIT License 开源协议。您可以自由使用、修改和分发本项目的代码，但需保留原始版权声明。

## 👨‍💻 贡献指南

欢迎提交 Issue 和 Pull Request！如果您发现 Bug 或有新功能建议，请随时反馈。

### 开发规范
- 遵循 PEP 8 Python 代码风格
- 所有视图函数使用类型提示（可选）
- 提交前运行 `python manage.py check` 检查配置
- 数据库迁移文件必须包含在提交中

## 📞 联系方式

如有问题或建议，欢迎通过以下方式联系：
- **邮箱**: 3302393536@qq.com
- **GitHub Issues**: [提交问题](https://github.com/yourusername/liuying/issues)

---
**用最扎实的技术，写最真实的博客。**

*最后更新时间: 2026年4月26日*
