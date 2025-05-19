FROM python:3.12.9-alpine

WORKDIR /app

# Install system dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    python3-dev \
    libffi-dev \
    openssl-dev \
    libstdc++ \
    bash

# Install Circus globally
RUN pip install --no-cache-dir circus

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose ports for API or WebSocket services
EXPOSE 8000

# No default CMD — use CMD or entrypoint in docker-compose.yml or override via CLI
