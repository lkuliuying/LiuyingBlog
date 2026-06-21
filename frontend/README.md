# 流萤博客 · 前端

Vue 3 + Vite + Element Plus + Pinia，纯 SPA，所有数据走 `/api`（开发期由 vite proxy 转到 `http://127.0.0.1:8000`）。

## 开发

```bash
cd frontend
npm install
npm run dev      # http://localhost:5173
```

## 构建

```bash
npm run build    # 输出到 dist/
```

生产环境用 Nginx 把 `dist/` 作为根路径静态站点，并把 `/api/`、`/media/` 交给 Django。管理后台由 `admin-frontend/dist/` 独立部署到 `/manage/`，Django Admin 已停用。

## 目录约定

- `src/api/`     — 按资源拆分的接口模块（auth/blog/comment）
- `src/stores/`  — Pinia store，目前只放鉴权信息
- `src/views/`   — 路由页面
- `src/components/` — 跨页面复用的组件
- `src/layouts/` — 通用布局（顶栏 + 主体 + 页脚）
- `src/types/`   — 共享 TypeScript 类型
