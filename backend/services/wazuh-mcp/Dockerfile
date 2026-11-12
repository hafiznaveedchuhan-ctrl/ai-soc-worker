# syntax=docker/dockerfile:1
# wazuh-mcp — multi-stage build (feature 09). Build from backend/:  docker build -f services/wazuh-mcp/Dockerfile -t ai-soc/wazuh-mcp:<sha> .
# Every line is explained in docs/LEARNING.md §12.

# ---- stage 1: build the virtual environment with uv (pinned image) ----
FROM ghcr.io/astral-sh/uv:0.12.6-python3.12-trixie-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=0
WORKDIR /app
# the whole workspace is needed so uv can resolve the lockfile; .dockerignore keeps secrets and tests out
COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable --package wazuh-mcp

# ---- stage 2: small runtime, non-root ----
FROM python:3.12-slim-trixie AS runtime
RUN groupadd --system --gid 10001 app && useradd --system --uid 10001 --gid app --no-create-home app \
    && mkdir -p /data && chown app:app /data
WORKDIR /app
COPY --from=builder --chown=app:app /app/.venv /app/.venv
COPY --chown=app:app evals/data/alerts /app/fixtures
ENV PATH="/app/.venv/bin:$PATH" PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
ENV WAZUH_FIXTURES_DIR=/app/fixtures WAZUH_HOST=0.0.0.0 WAZUH_PORT=8101
USER app
EXPOSE 8101
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 CMD python -c "import socket; socket.create_connection(('127.0.0.1', 8101), 2)"
CMD ["python", "-m", "wazuh_mcp"]
