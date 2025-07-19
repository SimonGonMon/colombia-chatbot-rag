# First, build the application in the `/app` directory
FROM ghcr.io/astral-sh/uv:bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_PYTHON_INSTALL_DIR=/python
ENV UV_PYTHON_PREFERENCE=only-managed

# Install Python before the project for caching
RUN uv python install 3.11

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

# Then, use a final image without uv
FROM debian:bookworm-slim

# Create app user
RUN useradd -ms /bin/bash app

# Copy the Python version
COPY --from=builder --chown=app:app /python /python

# Copy the application from the builder
COPY --from=builder --chown=app:app /app /app

# Ensure fastapi executable has correct permissions
RUN chmod +x /app/.venv/bin/fastapi

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Switch to non-root user
USER app

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["fastapi", "run", "--host", "0.0.0.0", "--port", "8000", "/app/src/api/main.py"]