# KitchenBook 快速部署指南

如果您想快速上手，按照以下步骤操作：

## 📋 前置要求

- Ubuntu 20.04/22.04 服务器
- 已有公网 IP
- 已安装 SSH（能登录服务器）

## 🚀 5 分钟快速部署

### 1. 连接服务器

```bash
ssh root@your_server_ip
```

### 2. 运行一键安装脚本

复制以下命令到服务器终端：

```bash
# 创建用户并切换
adduser kitchenbook
usermod -aG sudo kitchenbook
su - kitchenbook

# 安装必要软件
sudo apt update && sudo apt install -y git python3.11 python3.11-venv python3-pip \
    postgresql postgresql-contrib nginx nodejs npm curl

# 配置数据库
sudo -u postgres psql << EOF
CREATE DATABASE kitchenbook_db;
CREATE USER kitchenbook_user WITH PASSWORD 'ChangeMeToSecurePassword123!';
GRANT ALL PRIVILEGES ON DATABASE kitchenbook_db TO kitchenbook_user;
\q
EOF

# 克隆项目
cd ~
git clone https://github.com/linzhiqin2003/MyWeb.git KitchenBook
cd KitchenBook

# 安装后端
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
pip install gunicorn psycopg2-binary python-dotenv

# 创建环境变量
cat > backend/.env << EOF
SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
DEBUG=False
ALLOWED_HOSTS=your_server_ip
DB_ENGINE=django.db.backends.postgresql
DB_NAME=kitchenbook_db
DB_USER=kitchenbook_user
DB_PASSWORD=ChangeMeToSecurePassword123!
DB_HOST=localhost
DB_PORT=5432
CORS_ALLOWED_ORIGINS=http://your_server_ip
EOF

# 配置 Django
cd backend
mkdir -p logs
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser  # 按提示创建管理员账号
python manage.py seed_data  # 可选：填充示例数据

# 安装前端
cd ~/KitchenBook/frontend
npm install
npm run build

# 配置 Gunicorn 服务
sudo cp ~/KitchenBook/deploy/gunicorn.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start gunicorn
sudo systemctl enable gunicorn

# 配置 Nginx
sudo cp ~/KitchenBook/deploy/nginx.conf /etc/nginx/sites-available/kitchenbook
# 修改 nginx.conf 中的域名/IP
sudo sed -i 's/your_domain.com/your_server_ip/g' /etc/nginx/sites-available/kitchenbook
sudo ln -s /etc/nginx/sites-available/kitchenbook /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# 配置防火墙
sudo ufw allow 'OpenSSH'
sudo ufw allow 'Nginx Full'
sudo ufw --force enable

echo "🎉 部署完成！访问 http://your_server_ip 查看网站"
```

### 3. 验证部署

在浏览器访问：`http://your_server_ip`

### 4. 后续配置（可选）

**配置域名和 HTTPS：**

```bash
# 更新 Nginx 配置中的域名
sudo nano /etc/nginx/sites-available/kitchenbook
# 将 your_server_ip 替换为您的域名

# 重启 Nginx
sudo systemctl restart nginx

# 安装 SSL 证书
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your_domain.com -d www.your_domain.com
```

## 🔄 日常更新

创建自动部署脚本：

```bash
cd ~/KitchenBook
chmod +x deploy/deploy.sh
./deploy/deploy.sh
```

## 🐛 遇到问题？

查看日志：

```bash
# Gunicorn 日志
sudo journalctl -u gunicorn -f

# Nginx 日志
sudo tail -f /var/log/nginx/error.log

# Django 日志
tail -f ~/KitchenBook/backend/logs/gunicorn-error.log
```

检查服务状态：

```bash
sudo systemctl status gunicorn
sudo systemctl status nginx
```

---

**需要完整教程？** 查看 [DEPLOYMENT.md](DEPLOYMENT.md)
