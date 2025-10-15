#!/bin/bash

# Environment Setup Validator for ChatMinds
echo "🔍 ChatMinds Environment Validation"
echo "=================================="

# Check Docker
echo -n "Docker installed: "
if command -v docker &> /dev/null; then
    echo "✅ $(docker --version)"
else
    echo "❌ Not found"
    exit 1
fi

echo -n "Docker running: "
if docker info > /dev/null 2>&1; then
    echo "✅ Yes"
else
    echo "❌ No - Please start Docker Desktop"
    exit 1
fi

# Check Docker Compose
echo -n "Docker Compose: "
if command -v docker-compose &> /dev/null; then
    echo "✅ $(docker-compose --version)"
else
    echo "❌ Not found"
    exit 1
fi

# Check .env file
echo -n ".env file exists: "
if [ -f ".env" ]; then
    echo "✅ Yes"
    
    echo -n "OpenAI API Key set: "
    if grep -q "your_openai_api_key_here" .env; then
        echo "❌ Please update with your actual API key"
        echo "   Edit .env file and replace 'your_openai_api_key_here' with your OpenAI API key"
    else
        if grep -q "OPENAI_API_KEY=sk-" .env; then
            echo "✅ Yes (appears to be set)"
        else
            echo "⚠️  Set but format unclear - should start with 'sk-'"
        fi
    fi
else
    echo "❌ No - will be created automatically"
fi

# Check required directories
echo -n "Project structure: "
if [ -d "chatminds" ] && [ -d "chatminds-llm" ]; then
    echo "✅ Valid"
else
    echo "❌ Missing chatminds or chatminds-llm directories"
    exit 1
fi

# Check key files
echo -n "Required files: "
missing_files=()
for file in "docker-compose.dev.yml" "chatminds/Dockerfile.dev" "chatminds-llm/Dockerfile"; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -eq 0 ]; then
    echo "✅ All present"
else
    echo "❌ Missing: ${missing_files[*]}"
    exit 1
fi

# Check ports
echo -n "Port availability: "
ports_in_use=()
for port in 5000 8000; do
    if netstat -tuln 2>/dev/null | grep -q ":$port "; then
        ports_in_use+=("$port")
    fi
done

if [ ${#ports_in_use[@]} -eq 0 ]; then
    echo "✅ Ports 5000 and 8000 available"
else
    echo "⚠️  Ports in use: ${ports_in_use[*]} (will be handled by Docker)"
fi

echo ""
echo "🚀 Environment Status: READY"
echo ""
echo "Next steps:"
echo "1. Add your OpenAI API key to .env file (if not done)"
echo "2. Run: ./test_local.sh"
echo "3. Visit: http://localhost:5000"