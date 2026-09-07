#!/bin/bash

# KitchenBook 一键部署脚本
# 使用方法: ./deploy.sh

set -e  # 遇到错误立即退出

echo "🚀 开始部署 KitchenBook..."

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 进入项目目录
cd ~/KitchenBook

echo -e "${YELLOW}📦 1. 拉取最新代码...${NC}"
# 服务器上的 working tree 可能因为热补丁（直接 scp / sed）而处于 dirty 状态。
# 这种"本地改动"通常是上一次还没 commit 的紧急修复，commit 已经 push 上来后
# 用 git pull 会撞 "would be overwritten by merge" 报错并 abort 整个 deploy。
# 这里先把 dirty 都 stash（含 untracked），pull 完再尝试 pop —— 如果 pop 冲突
# （说明 stash 的内容已经被 origin 里的 commit 覆盖），就丢弃 stash，原 working
# tree 已经被 origin 的版本替代，正是想要的结果。
AUTOSTASHED=0

# stash 的恢复挂在 trap EXIT 上，而不是只写在 pull 之后的顺序流程里：
# `set -e` 下 git pull 一旦失败（这台机器到 github.com 的 443 偶尔超时）
# 脚本会当场退出，顺序流程里的 pop 根本轮不到执行，stash 就永远留在栈里。
# 服务器上因此积压过一个 2026-02-04 的孤儿 stash，直到 2026-09-07 才被发现。
restore_autostash() {
    [ "$AUTOSTASHED" = "1" ] || return 0
    AUTOSTASHED=0
    cd ~/KitchenBook || return 0   # trap 触发时 cwd 可能已经在 frontend/ 里
    if git stash pop 2>/dev/null; then
        echo -e "${YELLOW}↻ stash 已恢复（pull 不冲突）${NC}"
    else
        echo -e "${YELLOW}↻ stash 恢复冲突 → 已被 origin/main 取代，丢弃 stash${NC}"
        # pop 留下的冲突标记需要 reset 干净
        git checkout -- . 2>/dev/null || true
        git stash drop 2>/dev/null || true
    fi
}

if ! git diff --quiet || ! git diff --cached --quiet || [ -n "$(git ls-files --others --exclude-standard)" ]; then
    echo -e "${YELLOW}⚠️  working tree 有未提交改动，先 stash 让 pull 能跑${NC}"
    git stash push -u -m "deploy.sh autostash $(date -u +%FT%TZ)" || true
    AUTOSTASHED=1
    trap restore_autostash EXIT
fi
git pull --rebase=false origin main
restore_autostash
trap - EXIT

echo -e "${YELLOW}🐍 2. 激活虚拟环境...${NC}"
source venv/bin/activate

echo -e "${YELLOW}📚 3. 安装后端依赖...${NC}"
cd backend
pip install -q -r requirements.txt

echo -e "${YELLOW}🗄️  4. 运行数据库迁移...${NC}"
python manage.py migrate --noinput

echo -e "${YELLOW}📦 5. 收集静态文件...${NC}"
python manage.py collectstatic --noinput

echo -e "${YELLOW}🎨 6. 构建前端...${NC}"
cd ~/KitchenBook/frontend
npm install --silent
npm run build

echo -e "${YELLOW}🧾 6.1 构建 Receipts 前端...${NC}"
cd ~/KitchenBook/receipts-frontend
npm install --silent
npm run build

echo -e "${YELLOW}🌐 6.2 同步 Nginx 配置...${NC}"
# 仓库里的 deploy/nginx.conf 长期是「孤儿模板」：部署从不拷贝它，生产的
# /etc/nginx/conf.d/kitchenbook.conf 全靠手工 scp/sed 维护，两边随时可能悄悄分叉。
# 这里让它成为唯一事实来源，但只在真有差异时动手，且先备份、再 nginx -t，
# 校验不过立刻回滚 —— 宁可不部署，也不能把线上 nginx 改坏。
NGINX_SRC=~/KitchenBook/deploy/nginx.conf
NGINX_DST=/etc/nginx/conf.d/kitchenbook.conf
if [ ! -f "$NGINX_DST" ]; then
    echo -e "${RED}✗ 找不到 $NGINX_DST，跳过同步（请先确认生产 nginx 配置路径）${NC}"
elif sudo cmp -s "$NGINX_SRC" "$NGINX_DST"; then
    echo -e "${GREEN}✓ Nginx 配置已是最新，无需改动${NC}"
else
    NGINX_BAK="$NGINX_DST.bak.$(date -u +%Y%m%dT%H%M%SZ)"
    echo -e "${YELLOW}⚠️  检测到差异，备份到 $NGINX_BAK 后覆盖${NC}"
    sudo diff -u "$NGINX_DST" "$NGINX_SRC" || true
    sudo cp -p "$NGINX_DST" "$NGINX_BAK"
    sudo cp "$NGINX_SRC" "$NGINX_DST"
    if sudo nginx -t; then
        echo -e "${GREEN}✓ Nginx 配置校验通过${NC}"
    else
        echo -e "${RED}✗ Nginx 配置校验失败，已回滚到 $NGINX_BAK${NC}"
        sudo cp -p "$NGINX_BAK" "$NGINX_DST"
        sudo nginx -t || true
        exit 1
    fi
fi

echo -e "${YELLOW}🔄 7. 重启服务...${NC}"
# 游戏模块已下线；清理旧部署中可能仍启用的 Daphne 服务。
if systemctl list-unit-files daphne.service --no-legend 2>/dev/null | grep -q '^daphne.service'; then
    sudo systemctl disable daphne
    sudo systemctl stop --no-block daphne || true
    sleep 2
    if systemctl is-active --quiet daphne; then
        sudo systemctl kill --kill-who=all --signal=SIGKILL daphne || true
    fi
    sudo rm -f /etc/systemd/system/daphne.service
    sudo systemctl daemon-reload
fi
sudo systemctl restart gunicorn
sleep 2
sudo systemctl restart nginx

echo -e "${YELLOW}✅ 8. 检查服务状态...${NC}"
if systemctl is-active --quiet gunicorn; then
    echo -e "${GREEN}✓ Gunicorn 运行正常${NC}"
else
    echo -e "${RED}✗ Gunicorn 启动失败${NC}"
    sudo journalctl -u gunicorn -n 20
    exit 1
fi

if systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✓ Nginx 运行正常${NC}"
else
    echo -e "${RED}✗ Nginx 启动失败${NC}"
    sudo systemctl status nginx
    exit 1
fi

echo -e "${GREEN}🎉 部署完成！${NC}"
echo -e "访问您的网站: ${GREEN}https://$(hostname -I | awk '{print $1}')${NC}"
