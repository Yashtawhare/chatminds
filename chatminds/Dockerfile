# Multi-stage build for optimized production image
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt gunicorn

# Production stage
FROM python:3.11-slim

# Create non-root user for security
RUN groupadd -r chatminds && useradd -r -g chatminds chatminds

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy Python packages from builder stage
COPY --from=builder /root/.local /home/chatminds/.local

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=chatminds:chatminds . .

# Create necessary directories
RUN mkdir -p data logs static/uploads \
    && chown -R chatminds:chatminds /app

# Switch to non-root user
USER chatminds

# Add local bin to PATH
ENV PATH=/home/chatminds/.local/bin:$PATH

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Expose port
EXPOSE 5000

# Create startup script
COPY --chown=chatminds:chatminds start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Start application
CMD ["/app/start.sh"]