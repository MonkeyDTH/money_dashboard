# NAS 运维手册

## 基本信息

| 项目 | 值 |
|------|-----|
| 主机 | `thqnapnas.myqnapcloud.com` |
| SSH 端口 | `22333` |
| 用户 | `MonkeyDTH` |
| 项目路径 | `/share/TH/Projects/Personal/money_dashboard` |
| Docker 路径 | `/share/CACHEDEV1_DATA/.qpkg/container-station/bin/docker` |
| 服务访问地址 | `http://thqnapnas.myqnapcloud.com:7335` |

---

## SSH 登录

本地已配置免密登录（使用 `~/.ssh/id_ed25519`），直接连接：

```bash
ssh -p 22333 MonkeyDTH@thqnapnas.myqnapcloud.com
```

---

## 传输文件到 NAS

### 方法一：SCP（推荐，已启用 SFTP）

```bash
scp -P 22333 <本地文件> MonkeyDTH@thqnapnas.myqnapcloud.com:<目标路径>
```

**注意**：项目 `data/` 目录下的文件属主为 `admin`，MonkeyDTH 没有直接写入权限。
需先传到家目录，再用 sudo 移动：

```bash
# 第一步：传到家目录
scp -P 22333 ./data/money.db MonkeyDTH@thqnapnas.myqnapcloud.com:~/money.db

# 第二步：SSH 进去用 sudo 覆盖
ssh -p 22333 MonkeyDTH@thqnapnas.myqnapcloud.com
sudo cp ~/money.db /share/TH/Projects/Personal/money_dashboard/data/money.db
```

### 方法二：Windows 网络共享

在文件资源管理器地址栏输入 `\\thqnapnas`，直接拖拽文件。

---

## Docker 常用命令

以下命令在 NAS SSH 会话中、项目目录下执行：

```bash
cd /share/TH/Projects/Personal/money_dashboard

# 查看服务状态
sudo docker compose ps

# 重启服务
sudo docker compose restart

# 重新构建并启动（更新代码后）
sudo docker compose up -d --build

# 查看日志
sudo docker compose logs -f
```

---

## 更新数据库文件

本地数据库有更新时，同步到 NAS：

```bash
# 1. 传文件到家目录
scp -P 22333 D:/Projects/Personal/money_dashboard/data/money.db MonkeyDTH@thqnapnas.myqnapcloud.com:~/money.db

# 2. SSH 进去覆盖并重启
ssh -p 22333 MonkeyDTH@thqnapnas.myqnapcloud.com
sudo cp ~/money.db /share/TH/Projects/Personal/money_dashboard/data/money.db
cd /share/TH/Projects/Personal/money_dashboard
sudo docker compose restart
```

---

## 更新应用代码

```bash
# NAS 上拉取最新代码并重新构建
ssh -p 22333 MonkeyDTH@thqnapnas.myqnapcloud.com
cd /share/TH/Projects/Personal/money_dashboard
git pull
sudo docker compose up -d --build
```
