FROM docker.m.daocloud.io/python:3.11-slim

WORKDIR /app

# 安装 uv
COPY --from=ghcr.m.daocloud.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 先复制依赖文件，利用 Docker 层缓存
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# 复制源码
COPY app/ ./app/
COPY templates/ ./templates/
COPY static/ ./static/
COPY migrations/ ./migrations/
COPY alembic.ini ./

# 创建数据目录
RUN mkdir -p /app/data

EXPOSE 8000

CMD ["uv", "run", "sh", "-c", "alembic upgrade head && fastapi run app/main.py --port 8000 --host 0.0.0.0"]
