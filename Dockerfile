# Single-stage build optimized for ARM64
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements_ultra_minimal.txt requirements.txt

# Install Python dependencies directly with retry logic
RUN pip install --upgrade pip setuptools wheel --retries 3 --timeout 60 && \
    pip install --no-cache-dir --only-binary=all --retries 3 --timeout 60 -r requirements.txt

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
