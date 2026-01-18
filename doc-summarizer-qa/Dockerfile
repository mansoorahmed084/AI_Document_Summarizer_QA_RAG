# Multi-stage Dockerfile for AI Document Summarizer & Q&A Backend
# Stage 1: Build dependencies
FROM python:3.13-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime image
FROM python:3.13-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder to a location accessible by all users
COPY --from=builder /root/.local /usr/local

# Make sure scripts are usable
ENV PATH=/usr/local/bin:$PATH

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Copy application code (including frontend)
COPY --chown=appuser:appuser . .

# Expose port (Cloud Run uses PORT env var, default to 8080)
ENV PORT=8080
EXPOSE 8080

# Health check (use default port 8080 for health check)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run the application
# Cloud Run sets PORT environment variable, default to 8080
# Use --log-level info to see startup messages and errors
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080} --log-level info
