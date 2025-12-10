#!/bin/bash
# This script runs on first boot to set up the chat server

set -e

# Update system
echo "Updating system packages..."
dnf update -y

# Install Docker
echo "Installing Docker..."
dnf install -y docker

# Start Docker service
echo "Starting Docker service..."
systemctl start docker
systemctl enable docker

# Add ec2-user to docker group (for manual management if needed)
usermod -aG docker ec2-user

# Wait for Docker to be ready
sleep 5

# Pull and run the chat server
echo "Pulling Docker image: ${docker_image}"
docker pull ${docker_image}

echo "Starting chat server..."
docker run -d \
  --name chat-server \
  --restart unless-stopped \
  -p 1234:1234 \
  ${docker_image}

# Verify container is running
sleep 5
docker ps

echo "Chat server setup complete!"
echo "Server should be accessible on port 1234"

# Log output for debugging
docker logs chat-server
