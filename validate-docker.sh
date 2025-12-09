#!/bin/bash
# Docker Setup Validation Script

echo "=== Docker Setup Validation ==="
echo ""

# Check if files exist
echo "Checking required files..."
files=("Dockerfile" "Dockerfile.client" "docker-compose.yml" ".dockerignore" "src/server.py" "src/client.py" "src/protocol.py" "src/message_handler.py" "requirements.txt")

all_present=true
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file"
    else
        echo "✗ $file - MISSING!"
        all_present=false
    fi
done

echo ""

if [ "$all_present" = true ]; then
    echo "✅ All required files present!"
    echo ""
    echo "You can now run:"
    echo "  docker build -t chat-server:latest ."
    echo "  docker build -t chat-client:latest -f Dockerfile.client ."
    echo "  docker-compose up"
else
    echo "❌ Some files are missing. Please add them before building."
    exit 1
fi

echo ""
echo "=== Next Steps ==="
echo "1. Build images:       docker build -t chat-server:latest ."
echo "2. Test with compose:  docker-compose up"
echo "3. Push to Docker Hub: docker push yourusername/chat-server:latest"
