# Multi-stage build optimized for ARM64
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# No system dependencies needed - Python base image has everything we need

# Copy requirements first for better caching
COPY requirements_ultra_minimal.txt requirements.txt

# Install Python dependencies in a virtual environment with optimized caching
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip and install dependencies with better caching
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir --only-binary=all -r requirements.txt

# Production stage (ARM64 optimized)
FROM python:3.11-slim as production

# Set working directory
WORKDIR /app

# No system dependencies needed

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY . .

# Accept build arguments for API keys
ARG OPENAI_API_KEY
ARG ANTHROPIC_API_KEY

# Set environment variables for testing
ENV OPENAI_API_KEY=$OPENAI_API_KEY
ENV ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY
ENV CI=true

# Run tests during build (only if API keys are provided)
RUN if [ -n "$OPENAI_API_KEY" ] && [ -n "$ANTHROPIC_API_KEY" ]; then \
        echo "🧪 Running tests during build..." && \
        python test_installation.py; \
    else \
        echo "⚠️  Skipping tests (no API keys provided)"; \
    fi

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose ports
EXPOSE 8000 8501

# Health check using Python instead of curl
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Default command
CMD ["python", "main.py"]
