# Chat Server Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Expose the port the server listens on
EXPOSE 1234

# Set Python path
ENV PYTHONPATH=/app

# Run the server
CMD ["python", "-m", "src.server"]
