FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install runtime dependencies
RUN pip install --upgrade pip && \
    pip install asyncua

# Copy application code
COPY . /app

# Ensure certificates directory exists at runtime and run client
CMD ["bash", "-c", "mkdir -p certs && python cert.py && python client.py"]


