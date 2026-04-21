FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy dependency files and src code (required by pyproject.toml)
COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-install-project

RUN apt-get update && apt-get install -y \
    libxrender1 \
    libxext6 \
    libexpat1 \
    && rm -rf /var/lib/apt/lists/*

# Copy application code
COPY ./src ./src

CMD ["uv", "run", "shiny", "run", "src/app.py", "--host", "0.0.0.0", "--port", "8000"]