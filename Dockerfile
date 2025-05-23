FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
        libpq-dev \
        gcc \
        g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Install the package in editable mode
RUN pip install -e .

# Create necessary directories
RUN mkdir -p /app/logs /app/knowledge /app/data

# Create a non-root user
RUN useradd --create-home --shell /bin/bash golett \
    && chown -R golett:golett /app

# Switch to non-root user
USER golett

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["python", "-m", "uvicorn", "golett.api.main:app", "--host", "0.0.0.0", "--port", "8000"] 