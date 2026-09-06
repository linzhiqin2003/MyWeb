# MyWeb 项目记忆文件

> LZQ 个人综合平台，域名 www.lzqqq.org

## 技术栈

- **后端**: Django 5.2 + DRF | SQLite (开发) / PostgreSQL (生产)
- **主前端**: Vue 3 + Vite + Tailwind CSS + Vue Router + Axios
- **记账前端**: 独立 Vue 3 应用（JWT 认证）
- **部署**: Nginx + Gunicorn + Systemd

## 项目结构

```
MyWeb/
├── backend/                 # Django 后端（统一 API 服务）
│   ├── config/              #   Django 配置 (settings.py, urls.py, asgi.py)
│   ├── api/                 #   厨房系统：菜谱/订单/博客/AI对话
│   ├── accounts/            #   用户系统：JWT 认证 + 组织管理
│   ├── receipts/            #   记账系统：收据/分类/统计
│   ├── cards/               #   塔罗牌数据
│   ├── readings/            #   塔罗牌阵
│   ├── oracle/              #   塔罗占卜
│   ├── questions/           #   AI 出题模块
│   ├── common/              #   共享 DeepSeek 模型与客户端配置
│   └── media/               #   用户上传文件
├── frontend/                # 主前端（厨房/博客/塔罗/出题）
│   └── src/
│       ├── views/           #   页面组件
│       ├── components/      #   可复用组件（含 blog/ tarot/ 子目录）
│       ├── api/             #   API 客户端模块
│       ├── store/           #   状态管理 (auth.js, cart.js)
│       ├── config/          #   配置文件
│       └── router/          #   路由配置
├── receipts-frontend/       # 记账前端（独立应用，JWT 认证）
├── deploy/                  # 部署脚本与配置
└── docs/                    # 文档
```

## 后端 API 路由总览 (backend/config/urls.py)

| 路由前缀 | 应用 | 说明 |
|----------|------|------|
| `/api/` | api | 厨房：菜谱/食材/订单/博客/AI对话/会话管理 |
| `/api/questiongen/` | questions | AI 出题 |
| `/receipts/api/` | receipts + accounts | 记账系统 + 用户认证 |

## 前端路由模块 (frontend/src/router/index.js)

| 模块 | 路径前缀 | 说明 |
|------|---------|------|
| 首页 | `/` | 个人主页 (PortfolioHomeView) |
| 厨房 | `/kitchen/` | 菜谱浏览/点餐/厨师后台 |
| 博客 | `/blog/` | 技术博客（独立暗色主题） |
| 出题 | `/questiongen` | AI 出题系统 |
| 塔罗 | `/tarot/` | 塔罗占卜 |

厨师后台路由需 `meta: { requiresAuth: true, authType: 'chef' }`。

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
| `/login` | 登录 |
| `/register` | 注册 |
| `/invite/:id` | 接受邀请 |

## 认证机制

- **厨师认证**: SHA256 token，凭证在 settings.py 环境变量配置
- **记账系统认证**: JWT (rest_framework_simplejwt)，独立用户系统 + 组织管理

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

## 进展记录

### 2026-09-07
- **塔罗圣所对外开放**：`/tarot` 及 5 个子页此前全部缺 `meta.public`，访客一律被路由守卫踢到 `/login`——整个模块对外是关着的（commit `2cbe4ec`）
- 后端本来就允许匿名：`settings.py` 无 `REST_FRAMEWORK` 配置 → DRF 默认 `AllowAny`；`Reading` 按 `session_key` 存、不挂用户。**加 `meta.public` 即可，后端不用动**
- **本地 main 曾落后 origin/main 4 个提交**（PR #3 只在远端和服务器上，本地从没 pull）。rebase 对齐，手工解掉 `deploy/nginx.conf` 冲突：保留 `/mystic/`，接上拆分后的 `/login` + `/tarot` location
- **今日神谕改按访客本地日期取牌**（commit `47d1e1c`）：Django 会把进程 TZ 设成 `settings.TIME_ZONE`（= UTC），所以 `oracle/views.py` 的 `date.today()` 返回 UTC 日期，UTC+8 用户每天 08:00 前拿到的都是昨天那张牌。改在前端传 `localToday()` 给已有的 `?date=` 参数，**不动 `TIME_ZONE`**（会牵连记账/博客所有时间显示）
- **`deploy.sh` 接管 nginx 配置**（commit `9bc9aad`，新增 6.2 步）：`deploy/nginx.conf` 长期是孤儿模板，生产 conf 全靠手工维护（十几个 `.bak` 为证）。现在仅在 `cmp` 检出差异时备份 + 覆盖 + `nginx -t`，校验不过立刻回滚并 `exit 1`。首次同步只改掉一行过时注释，说明此前无实质漂移
- ⚠️ **坑**：`bash deploy/deploy.sh` 会在第 1 步 git pull 换掉脚本自己，但这一轮 bash 读的仍是已打开的旧文件——**给 deploy.sh 加的新步骤要下一次部署才生效**。改部署脚本记得连跑两轮
- 本地环境：`venv/` 原本不存在（CLAUDE.md 里的 `source ../venv/bin/activate` 是空指令），用 `uv` 建了 Python 3.12 环境；本地库补跑 `readings.0003/0004` + `import_cards`（原本 0 张牌）
- 线上验证：6 页匿名直达无重定向；`/tarot/codex` 85 张图 0 broken；`/daily` 显示本地日期且随 `?date=` 换牌
- **凯尔特十字有张牌翻不出来**（commit `d943c32`）：「挑战」与「现状」同坐标、`z-index 20` 横压。真凶不是那张牌，而是 `.layout-piece` ——纯定位用的透明容器把 label 和卡牌一起撑成远大于卡牌的盒子，吞掉下层点击。命中测试实测「现状」只有 **9.5%** 面积可达（672 个采样点里 608 个被挡）
- 处方：定位容器 `pointer-events: none`，只给 `.card-rotator` `auto`；再让**已翻开的牌退出命中测试**（`revealCard` 对已翻开的牌本就直接 return）→ 同一位置连点两下依次翻出两张，不用去够那条十几像素的窄边。桌面 / 手机 375×812 / 线上均验证
- 顺带发现 `.overlay-card` 是**从未定义样式的死类名**（只在 SpreadLayout 里绑定），留着未动

### 2026-08-19
- **塔罗圣所 PR #3 已审、合并并部署**：https://github.com/linzhiqin2003/MyWeb/pull/3 → merge `7660d54`
- 新玩法：12 种牌阵、今日神谕、是非一问、星图典藏、占卜手记；正逆位；像素占卜师 HUD
- 服务器：`readings.0003/0004` migrate 成功（12 个牌阵），双前端 build + gunicorn/nginx 已重启
- 生产 nginx 补了 `/mystic/`（`deploy.sh` 不会拷 conf）；牌背/装饰图 `https://www.lzqqq.org/mystic/` 已 200
- 冒烟：`/api/tarot/daily/`、`/api/tarot/spreads/`（12）、愚者中文牌意覆盖均正常
- 未合：#1（draft + 冲突，首页已改版）、#2（仅文档）、#4（DeepSeek harness submodule，无生产影响）
- 已知：塔罗路由未标 `meta.public`，访客会被 JWT 守卫踢去 `/login`（与现有 `/tarot` 行为一致）

### 2026-08-04
- **首页改版原型 v0.2**（不影响主站）：`prototype/index.html` 单文件原型，`python3 -m http.server 8899 --directory prototype` 本地预览
- 三个场景：① Hero——生成头像 + WebGL 流体涟漪 + 鼠标追光/3D 倾斜 + 眨眼 Mascot + 全屏关键词词场；② AI 情报站——Coverflow 式 3D 轮播（中卡正对、两侧倾角扇形），滚动驱动 + 吸附（Demo 数据，待接新闻 Agent）；③ 足迹——WebGL 形变转场 + 全屏展开 + 场景切换 + 鼠标涟漪；④ 尾页——双行跑马灯 + 编辑式链接行 + 描边巨字
- v0.2 反馈修正：名字为「林智勤」；词云取消圆角卡片，改为大小字混排/描边/深度视差的自由词场；轮播按参考图改 Coverflow 而非整圈圆环
- 再迭代：情报页去呼吸灯→左侧编辑栏 + SIGNAL 描边水印；轮播改螺旋阶梯（绕竖轴 40°/级、下沉 56px/级、滚动驱动）；词场动态=鼠标斥力物理（170px 斥开+弹簧回位）+ 同组词库定时翻转换词（POOLS）
- 占位图（头像 + 3 张旅行照）AI 生成于 `prototype/assets/`，等用户提供真实旅行照片与 Sprite 素材后替换
- 技术：原生 WebGL shader（无 Three.js）、GSAP ScrollTrigger pin/snap、Lenis 平滑滚动、降级方案（no-gsap/no-webgl）
- 注意：无头浏览器（SwiftShader）对该页截图易挂起，验证用 `browser_evaluate` 读 DOM/transform 即可；真实浏览器无此问题

### 2026-06-08
- **Receipts 登录/注册页**：统一为 SaaS 分栏 UI；共享 `AuthHeroPanel` + `styles/auth-page.css`
- **AI Lab 下线**：移除前后端 AI Lab 模块、Hermes/docker 部署产物及相关 migration
- **课程文件**：迁移至 `archive/course-files/`
- **部署**：commit `5319ba1` 已推送；服务器 migrate + 双前端 build 完成，gunicorn/daphne/nginx 已重启
- **注意**：服务器若存在 `deploy.sh` 本地改动，stash pop 可能恢复旧版（含 Hermes 步骤）；部署后需 `git checkout -- deploy/deploy.sh`
