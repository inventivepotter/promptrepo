# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment to prod
ENV ENVIRONMENT=production

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy pyproject.toml, then install build backend
COPY pyproject.toml ./
COPY README.md ./

RUN pip install --no-cache-dir hatchling
RUN pip install --no-cache-dir .

# Copy application code
COPY . .

# Expose port
EXPOSE 7768

# Run the application
CMD ["python", "main.py"]