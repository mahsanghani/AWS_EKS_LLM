apiVersion: v1
kind: ConfigMap
metadata:
  name: dockerfile
  namespace: llm-deployment
data:
  Dockerfile: |
    FROM python:3.10-slim
    
    # Install system dependencies
    RUN apt-get update && apt-get install -y \
        gcc \
        g++ \
        curl \
        && rm -rf /var/lib/apt/lists/*
    
    # Set working directory
    WORKDIR /app
    
    # Copy requirements first for better caching
    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt
    
    # Copy application code
    COPY main.py .
    
    # Create non-root user
    RUN groupadd -r appuser && useradd -r -g appuser appuser
    RUN chown -R appuser:appuser /app
    USER appuser
    
    # Expose port
    EXPOSE 8000
    
    # Health check
    HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
        CMD curl -f http://localhost:8000/health || exit 1
    
    # Run the application
    CMD ["python", "main.py"]