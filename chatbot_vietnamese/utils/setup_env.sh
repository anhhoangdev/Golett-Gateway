#!/bin/bash

# Setup script for Vietnamese Farm Chatbot
# Script thiết lập cho Chatbot Nông nghiệp Việt Nam

echo "🌱 THIẾT LẬP CHATBOT NÔNG NGHIỆP VIỆT NAM 🌱"
echo "================================================"

# Check if .env file exists
if [ -f ".env" ]; then
    echo "📄 Tìm thấy file .env hiện có"
    read -p "Bạn có muốn ghi đè không? (y/N): " overwrite
    if [[ $overwrite != "y" && $overwrite != "Y" ]]; then
        echo "✅ Giữ nguyên cấu hình hiện tại"
        exit 0
    fi
fi

echo "🔧 Tạo file cấu hình .env..."

# Create .env file
cat > .env << 'EOF'
# Vietnamese Farm Chatbot Configuration
# Cấu hình Chatbot Nông nghiệp Việt Nam

# OpenAI API Key (Required)
OPENAI_API_KEY=your-openai-api-key-here

# Database Configuration
POSTGRES_CONNECTION=postgresql://postgres:password@localhost:5432/golett

# Vector Database
QDRANT_URL=http://localhost:6333

# CubeJS Configuration
CUBEJS_API_URL=http://localhost:4000/cubejs-api/v1
CUBEJS_API_TOKEN=your-cubejs-token-here
CUBEJS_SCHEMAS_PATH=cubejs/model/cubes

# Knowledge Base
KNOWLEDGE_FILE_PATH=farm_data/farm_business_domain_knowledge_vietnamese.md

# LLM Configuration
LLM_MODEL=gpt-4o

# User Configuration
USER_ID=interactive_user
EOF

echo "✅ Đã tạo file .env"
echo ""
echo "📝 HƯỚNG DẪN THIẾT LẬP:"
echo "1. Chỉnh sửa file .env và điền thông tin thực tế:"
echo "   - OPENAI_API_KEY: API key từ OpenAI"
echo "   - POSTGRES_CONNECTION: Chuỗi kết nối PostgreSQL"
echo "   - CUBEJS_API_TOKEN: Token từ CubeJS (nếu có)"
echo ""
echo "2. Đảm bảo các dịch vụ đang chạy:"
echo "   - PostgreSQL (port 5432)"
echo "   - Qdrant (port 6333)"
echo "   - CubeJS API (port 4000)"
echo ""
echo "3. Chạy chatbot:"
echo "   python chatbot_vietnamese/interactive_chat.py"
echo ""
echo "🚀 Chúc bạn sử dụng chatbot hiệu quả!" 