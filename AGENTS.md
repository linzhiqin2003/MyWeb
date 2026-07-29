# MyWeb 项目记忆文件

> LZQ 个人综合平台，域名 www.lzqqq.org

## 技术栈

- **后端**: Django 5.2 + DRF | SQLite (开发) / PostgreSQL (生产)
- **主前端**: Vue 3 + Vite + Tailwind CSS + Vue Router + Axios
- **记账前端**: 独立 Vue 3 应用（JWT 认证）
- **部署**: Nginx + Gunicorn + Systemd（纯 WSGI，无 WebSocket）

## 项目结构

```
MyWeb/
├── backend/                 # Django 后端（统一 API 服务）
│   ├── config/              #   Django 配置 (settings.py, urls.py, asgi.py)
│   ├── api/                 #   厨房系统：菜谱/订单/博客/AI 对话/OCR/转写
│   ├── accounts/            #   用户系统：JWT + Google 登录 + 组织管理
│   ├── receipts/            #   记账系统：收据/分类/统计
│   ├── cards/               #   塔罗牌数据
│   ├── readings/            #   塔罗牌阵
│   ├── oracle/              #   塔罗占卜
│   ├── questions/           #   AI 出题模块
│   ├── common/              #   共享 DeepSeek 模型与客户端配置 (deepseek_models.py)
│   └── media/               #   用户上传文件
├── frontend/                # 主前端（首页/厨房/博客/塔罗/出题）
│   └── src/
│       ├── views/           #   页面组件（含 tarot/ 子目录）
│       ├── components/      #   可复用组件（含 blog/ tarot/ 子目录）
│       ├── api/             #   API 客户端模块 (client.js, questiongen.js, tarot.js)
│       ├── store/           #   状态管理 (auth.js, cart.js)
│       ├── config/          #   配置文件 (api.js)
│       ├── assets/sprites/  #   首页像素精灵图（走 Vite 打包，不要放回 public/）
│       └── router/          #   路由配置
├── receipts-frontend/       # 记账前端（独立应用，JWT 认证）
├── archive/                 # 归档资料（课程文件等，不参与构建）
├── deploy/                  # 部署脚本与配置
└── docs/                    # 文档（prototypes/ 存首页设计原型）
```

## 后端 API 路由总览 (backend/config/urls.py)

| 路由前缀 | 应用 | 说明 |
|----------|------|------|
| `/api/` | api | 厨房：菜谱/食材/订单/博客/AI 对话/OCR；`/api/tarot/` 转发塔罗三应用 |
| `/api/questiongen/` | questions | AI 出题 |
| `/api/auth/` | accounts | 主站认证：注册/登录/Google/刷新/组织 |
| `/receipts/api/auth/` | accounts | 记账前端复用同一套认证端点 |
| `/receipts/api/` | receipts | 记账系统 |

## 前端路由模块 (frontend/src/router/index.js)

| 模块 | 路径前缀 | 说明 |
|------|---------|------|
| 首页 | `/` | 个人主页 PortfolioHomeView（像素云海 hero，公开） |
| 登录 | `/login` | AuthView（公开） |
| 厨房 | `/kitchen/` | 菜谱浏览/点餐/厨师后台 |
| 博客 | `/blog/` | 技术博客（独立暗色主题） |
| 出题 | `/questiongen` | AI 出题系统 |
| 塔罗 | `/tarot/` | 塔罗占卜 |

路由守卫规则：只有 `meta.public === true` 的 `/` 和 `/login` 免登录，其余全部需要 JWT；
厨师后台再加一层，`meta: { requiresAuth: true, authType: 'chef' }` 会走 `checkChefAuth()`，
不通过则跳 `/kitchen/chef/login`。

### 记账前端路由 (receipts-frontend/src/router/index.ts)

独立 Vue 应用，部署在 `/receipts/` 路径下，JWT 认证。

| 路径 | 说明 |
|------|------|
| `/` | 仪表盘统计 |
| `/upload` | 上传收据 |
| `/receipts` | 收据列表 |
| `/receipts/:id` | 收据详情 |
| `/profile` | 个人资料 |
| `/org-settings` | 组织管理 |
| `/login` | 登录（public） |
| `/register` | 注册（public） |
| `/invite/:id` | 接受邀请（public） |

## 认证机制

- **主站/记账认证**: JWT (rest_framework_simplejwt)，共用 `accounts` 应用；
  另支持 Google 登录（django-allauth socialaccount + `GoogleLoginView`）
- **厨师认证**: SHA256 token，凭证在 settings.py 环境变量配置（JWT 之上的第二层）
- **组织管理**: 组织 / 成员 / 邀请链接均在 `accounts` 应用下

## 开发命令

```bash
# 后端
cd backend && source ../venv/bin/activate
python manage.py runserver          # http://127.0.0.1:8000
python manage.py makemigrations && python manage.py migrate

# 主前端
cd frontend && npm run dev          # http://localhost:5173

# 记账前端
cd receipts-frontend && npm run dev # http://localhost:5174
```

## 开发注意事项

- 修改模型后必须 `makemigrations` + `migrate`
- 新增 API 字段需同步更新 serializers.py 的 `fields`
- 前端 API 地址通过 `config/api.js` 统一管理，生产环境使用相对路径
- Vite 开发代理已配置 `/api` 和 `/media` 转发到后端
- 样式使用 Tailwind，厨房模块 emerald/amber/stone 配色，博客模块紫色暗色主题
- LLM 调用统一走 `backend/common/deepseek_models.py`，换模型只改这一处
- 项目已无 WebSocket 栈（channels/daphne 已移除），实时需求需重新引入依赖

## 服务器部署

- **域名**: www.lzqqq.org
- **连接**: `ssh myserver`
- **部署脚本**: `deploy/` 目录（deploy.sh, nginx.conf, gunicorn.service 等）
- **服务器上已有项目和部署脚本**，每次代码更新后需要重新部署

### 部署流程

1. 本地完成开发，构建前端：
   ```bash
   cd frontend && npm run build
   cd receipts-frontend && npm run build
   ```
2. 推送代码到远程仓库
3. SSH 到服务器执行部署脚本：
   ```bash
   ssh myserver
   cd ~/MyWeb  # 或项目实际路径
   git pull
   bash deploy/deploy.sh
   ```

## 历史沿革（避免误判为「代码丢失」）

2026-06 至 2026-07 做过一次大规模瘦身，以下模块是**主动删除**的，不是遗漏：

- **AI Lab**（`5319ba1`）：前端 `components/ailab/` + 5 个 AiLab 视图、后端 `mcp_server/`、
  `deploy/docker/` 与 `deploy/hermes-patches/` 全部移除
- **废弃模块**（`d137c0e`）：`backend/apps/`（五子棋游戏 / 同声传译 / 表情包生成）、
  `backend/common/providers/` 多 LLM 提供商抽象、`backend/credits/`、iOS 项目、
  `gpu_server_patch/`；同时退役 channels/daphne/dashscope/groq/cerebras 依赖
- **首页改版**（`2150134`、`5cd2416`）：PortfolioHomeView 重写为像素云海 hero，
  精灵图从 `public/` 迁到 `src/assets/sprites/` 以获得打包哈希缓存
