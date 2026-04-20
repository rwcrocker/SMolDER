FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy dependency files and README (required by pyproject.toml)
COPY pyproject.toml uv.lock README.md ./

RUN uv sync --frozen --no-install-project

# Copy application code
COPY smolder ./smolder

CMD ["uv", "run", "shiny", "run", "smolder/app.py", "--host", "0.0.0.0", "--port", "8000"]