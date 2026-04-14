# 🌟 流萤博客

一个基于 Django 6.0 构建的生产级个人博客系统。本项目不仅实现了完整的业务闭环，还在架构上预留了标准的 RESTful API 扩展能力。没有过度设计，但每一处细节都经受了云服务器生产环境的严苛检验。

## 🛠️ 技术栈

- **后端核心**：Python 3.14 + Django 6.0.4
- **接口规范**：Django REST Framework (DRF)
- **前端展现**：HTML5 / CSS3 / Bootstrap 5
- **前端交互**：原生 JavaScript (Fetch API) + 局部 jQuery (AJAX)
- **富文本编辑**：WangEditor V5 (支持图片直传服务器)
- **数据存储**：SQLite 3 (针对读多写少场景的最优解)
- **服务器环境**：CentOS 9 + 宝塔面板
- **Web 服务**：Nginx (反向代理 + 静态资源托管)
- **WSGI 服务**：Gunicorn + Systemd (进程守护)

## ✨ 核心功能

### 👤 用户系统 (极致的交互体验)
- **无刷新头像上传**：悬浮遮罩触发，即时预览并处理浏览器缓存。
- **信息无感修改**：用户名、邮箱采用 Fetch API 异步修改，修改后页面顶部信息实时同步刷新。
- **安全密码重置**：修改密码后使用 `update_session_auth_hash` 保持登录态不掉线。
- **数据归集中心**：个人中心聚合展示发布的博客（可跳转详情）与历史评论（可溯源至原文章）。

### ✍️ 博客系统 (所见即所得)
- **WangEditor 深度集成**：完美解决 V5 版本外部 JS 引入与配置陷阱。
- **智能文件管理**：后端统一接收接口，按`年/月`划分目录，UUID 重命名防冲突。
- **首页封面提取**：后端 Model 增加 `@property` 方法，使用正则从 HTML 中智能提取第一张图作为卡片封面。

### 🛡️ 后台管理
- 引入 `django-jazzmin` 实现 Bootstrap 4 现代化响应式 UI。
- 深度定制 `admin.py`，配置列表过滤、搜索和自定义截断展示。

### 🔌 接口层预留
- 编写 `BlogSerializer`，将底层模型转化为规范的 JSON 格式。
- 独立编写 `api_views.py`，实现首页博客列表的 API 化，并接入 DRF 标准分页器。

## 📂 项目目录结构

```text
www/wwwroot/liuying/
├── liuyingblog/            # 项目全局配置
│   ├── settings.py         # 核心配置 (DEBUG=False, ALLOWED_HOSTS, DRF等)
│   ├── urls.py             # 主路由分发
│   └── __init__.py         # PyMySQL 版本兼容配置
│
├── blog/                   # 核心业务应用
│   ├── models.py           # 数据模型 (含首图提取属性)
│   ├── views.py            # 视图层 (网页渲染、文件上传)
│   ├── api_views.py        # DRF 接口视图 (API数据分发)
│   ├── serializers.py      # DRF 序列化器 (数据清洗)
│   ├── admin.py            # 后台管理深度定制
│   └── urls.py             # 业务路由
│
├── liuyingauth/            # 用户认证应用
│   └── views.py            # 登录、个人中心、信息修改
│
├── static/                 # 静态资源 (由 collectstatic 收集)
│   ├── wangeditor/         # 富文本编辑器 JS/CSS
│   └── js/pub_blog_new.js  # 博客发布前端逻辑
│
├── media/                  # 用户上传文件 (Nginx 直接托管)
│   ├── avatars/            # 用户头像
│   └── upload/             # 博客图片
│
├── venv/                   # Python 虚拟环境
├── db.sqlite3              # 数据库文件
└── gunicorn_ctl            # Gunicorn 控制脚本
```

## 🏗️ 架构设计理念

1. **"务实"的混合架构**
   拒绝为了炫技而盲目进行"前后端分离"。主站采用 Django Template 渲染，保证了极佳的 SEO 和首屏加载速度（对博客至关重要）；同时通过 DRF 平行构建了一套 RESTful API，未来无论是接入微信小程序还是大模型 AI，都不需要重构底层。

2. **"克制"的数据库选型**
   基于博客"读多写少"的业务模型，坚持使用 SQLite，避免了引入额外中间件（如 MySQL/Redis）的运维成本，单文件备份极其方便。

3. **"防御性"的 Nginx 配置**
   针对宝塔面板默认反向代理 `location ^~ /` 导致的"静态文件拦截死锁"问题，精准使用 `location ^~ /static/` 和 `location ^~ /media/` 提升优先级，实现了静态资源由 Nginx 高效托管，动态请求由 Django 处理的完美解耦。

## 🚀 本地快速运行

```bash
# 1. 克隆项目 (示例)
git clone <your-repo-url>
cd liuying

# 2. 创建并激活虚拟环境
python -m venv venv
source venv/bin/activate  # Windows下使用 venv\Scripts\activate

# 3. 安装依赖
pip install django djangorestframework django-jazzmin

# 4. 执行数据库迁移
python manage.py migrate

# 5. 创建超级管理员
python manage.py createsuperuser

# 6. 收集静态文件
python manage.py collectstatic

# 7. 启动开发服务器
python manage.py runserver
```

访问 `http://127.0.0.1:8000/` 即可查看首页，访问 `/admin/` 查看美化后的后台。

## 💡 踩坑记录

本项目非教程照搬，所有坑均在实战中解决：

- **Python 3.14 的坑**：Django 6.0 严格校验 MySQL 驱动版本，使用 PyMySQL 必须在 `__init__.py` 中伪装版本号才能绕过校验。
- **WangEditor V5 的坑**：配置项名极其严格，`MENU_CONF` 拼写错误会导致静默失败；其默认 2MB 上传限制需手动通过 `maxFileSize` 解除。
- **生产环境 `DEBUG=False` 的连环坑**：关闭 Debug 不仅引发 400 错误，还会导致 Django 拒绝服务静态/媒体文件，必须配合 `collectstatic` 和严谨的 Nginx `alias` 规则。
- **浏览器缓存坑**：修改外部引用的 JS 文件后，必须通过更改 `<script src="...?v=x">` 的版本号来强制客户端更新，否则极易产生"代码没生效"的错觉。
- **本地访问报错**：如果访问 `http://127.0.0.1:8000/` 出现"URL拼写可能存在错误，请检查"的提示，请确认：
  1. Django开发服务器是否正常启动
  2. 项目主路由 `liuyingblog/urls.py` 中是否正确配置了首页路由
  3. 浏览器是否有缓存问题，尝试强制刷新（Ctrl+F5）

## 📄 许可证

MIT License

---
**用最扎实的技术，写最真实的博客。**

---
