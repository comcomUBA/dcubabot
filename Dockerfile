FROM python:3.11-slim as builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Configure UV for container environment
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies (creates an isolated virtual environment at /app/.venv)
RUN uv sync --frozen --no-install-project --no-dev

FROM gcr.io/distroless/python3-debian12

WORKDIR /app

# Copy the dependencies from the builder's virtual environment
COPY --from=builder /app/.venv/lib/python3.11/site-packages /app/packages

COPY . .

ENV PYTHONPATH=/app/packages

ENTRYPOINT ["python"]
CMD ["main.py"]
