# syntax=docker/dockerfile:1

FROM python:3.11-slim AS base

# Set working directory
WORKDIR /app

# --- Builder stage: install dependencies into a venv ---
FROM base AS builder

# Install system dependencies (if any are needed for pip or runtime)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt first for better cache usage
COPY --link requirements.txt ./

# Create virtual environment and install dependencies using pip cache
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m venv .venv && \
    .venv/bin/pip install --upgrade pip && \
    .venv/bin/pip install -r requirements.txt

# Copy application code (app.py, wsgi.py, and any other needed files)
COPY --link app.py wsgi.py ./

# --- Final stage: minimal runtime image ---
FROM base AS final

# Create a non-root user
RUN adduser --disabled-password --gecos '' appuser

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code from builder
COPY --from=builder /app/app.py /app/app.py
COPY --from=builder /app/wsgi.py /app/wsgi.py

# Copy requirements.txt for reference (optional, not needed for runtime)
COPY --from=builder /app/requirements.txt /app/requirements.txt

# Set environment so venv is used
ENV PATH="/app/.venv/bin:$PATH"

# Use non-root user
USER appuser

# Expose the default port (optional, for documentation)
EXPOSE 5000

# Default command: use gunicorn with wsgi:app
CMD ["gunicorn", "wsgi:app", "--bind", "0.0.0.0:5000"]
