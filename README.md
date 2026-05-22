# 家庭资产看板

个人/家庭财务数据管理工具。月底定期录入，长期趋势一眼看清。

## 核心功能

- **资产快照** — 每月底录入各账户余额（活期、定期、基金、股票、公积金、房产等），自动生成净资产时间序列
- **看板首页** — 净资产趋势折线图、资产配置环形图、近 12 个月收入柱状图
- **账户管理** — 支持家庭共同 / 个人账户，含资产和负债类型，可停用已销户账户
- **薪资记录** — 按月录入薪资明细（基本工资、奖金、五险一金、个税等），实时计算应发 / 实发
- **公司管理** — 记录职业经历，跳槽后的收入挂在各自公司下
- **数据导出** — 一键导出全库 Excel（accounts / snapshots / companies / salaries / salary_items 多 sheet）

## 技术框架

| 层 | 选型 |
|----|------|
| 后端 | FastAPI + Jinja2（服务端渲染） |
| 数据库 | SQLite，ORM 用 SQLModel，迁移用 Alembic |
| 前端交互 | HTMX（局部刷新）+ Alpine.js（轻状态） |
| 样式 | Tailwind CSS CDN + ECharts CDN |
| 部署 | Docker Compose，SQLite 文件挂卷持久化 |
| 依赖管理 | uv |

## 目录结构

```
money_dashboard/
├── app/
│   ├── main.py          # FastAPI 入口
│   ├── deps.py          # 共享依赖（templates 实例）
│   ├── database.py      # 引擎、Session
│   ├── config.py        # 配置项
│   ├── seed.py          # 初始数据
│   ├── models/          # SQLModel 实体
│   ├── routers/         # 路由（按业务模块）
│   └── utils/           # 工具函数（模板过滤器等）
├── templates/           # Jinja2 模板
│   ├── base.html        # 全局布局（含 CDN 引入）
│   ├── partials/        # HTMX 局部片段
│   ├── dashboard/
│   ├── accounts/
│   ├── snapshots/
│   ├── salaries/
│   ├── companies/
│   └── data_io/
├── migrations/          # Alembic 迁移
├── data/                # SQLite 文件（运行时生成，已 gitignore）
├── docs/设计方案/        # 设计文档
├── Dockerfile
└── docker-compose.yml
```

## 启动

### 本地开发

```bash
# 安装依赖
uv sync

# 运行数据库迁移
uv run alembic upgrade head

# 启动开发服务器（含热重载）
uv run fastapi dev app/main.py --port 8003 --host 0.0.0.0
```

访问 http://localhost:8003

### Docker 部署

```bash
# 构建并启动（amd64）
docker compose up -d

# 查看日志
docker compose logs -f

# 停止
docker compose down
```

数据文件保存在宿主机 `./data/money.db`，更新镜像不会丢失数据。
