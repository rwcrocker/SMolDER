FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy dependency files and README (required by pyproject.toml)
COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-install-project

# Copy application code
COPY ./src ./src

# Ensure default artifact directory exists (can be overridden by volume mounts)
RUN mkdir -p /app/data