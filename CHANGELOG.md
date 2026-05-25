# Changelog

## [0.1.2] - 2026-05-25

### Added
- 飞书 Base 薪资历史导入脚本，一次性将 91 条历史记录写入本地数据库
- 自动创建爱奇艺 / 阿里 / 友塔三家公司记录，含就职时间区间
- 薪资明细拆分为 427 条 SalaryItem（合同工资、奖金、补贴、五险一金个人、个税、公积金充值）

## [0.1.1] - 2026-05-25

### Added
- NAS 运维手册（SSH 免密登录、文件传输、Docker 常用命令）

### Changed
- Docker 基础镜像和 uv 镜像切换为 DaoCloud 国内代理
- Python 依赖安装改用清华 PyPI 镜像，启用 BuildKit 缓存加速构建
- 服务对外端口改为 7335

## [0.1.0] - 2026-05-25

### Added
- FastAPI + Jinja2 + HTMX + Alpine.js + Tailwind CDN 全栈工程骨架，Docker Compose 一键部署
- 核心数据模型：Member / Account / AccountSnapshot / Company / SalaryRecord / SalaryItem / ExpenseCategory / MonthlyExpense，Alembic 管理迁移
- 账户管理（增删改停用，支持家庭共同/个人归属，含负债类型）
- 月度余额批量录入，支持一键复制上月数据
- 公司管理（职业经历，支持跳槽多公司）
- 薪资明细录入（动态明细项，实时计算应发/实发）
- 看板首页：净资产趋势折线图、资产配置环形图、近 12 个月收入柱状图（ECharts）
- 家庭 / 个人双视图切换（URL 参数驱动，图表独立计算）
- 账户列表、余额录入页按"家庭共同 / 个人"分组展示
- Excel 全库导出（accounts / snapshots / companies / salaries / salary_items 多 sheet）
- 一次性历史数据导入脚本：7 个个人账户 + 68 个月 408 条余额快照（2020-05 至 2026-04）

### Fixed
- Jinja2 HTML 转义导致 ECharts 图表空白，对 JSON 变量加 `| safe` 过滤器
