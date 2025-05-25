# 🇻🇳 Interactive Vietnamese Business Intelligence Chatbot

An intelligent Vietnamese chatbot with **context awareness** and **memory integration** that can answer business questions using CubeJS data.

## 🚀 Quick Start

### Method 1: Using the Launcher Script
```bash
cd /home/anhhoangdev/AgenticAi/Golett-Gateway
python chatbot_vietnamese/start_chat.py
```

### Method 2: Direct Execution
```bash
cd /home/anhhoangdev/AgenticAi/Golett-Gateway
python chatbot_vietnamese/core/vietnamese_chatbot.py
```

## 🧠 Context Awareness Features

### **Memory Integration**
- **Session Memory**: Remembers conversations within the current chat session
- **Cross-Session Memory**: Stores conversations across different sessions (with Golett AI)
- **Context Building**: Uses previous conversations to provide better answers
- **Similar Conversation Search**: Finds related past discussions

### **Smart Context Usage**
- **Topic Tracking**: Remembers what topics you've discussed
- **Cube Usage History**: Tracks which data cubes you've used
- **Measure Preferences**: Learns your preferred metrics
- **Business Intelligence**: Extracts insights from conversation patterns

## 💬 Interactive Commands

During the chat session, you can use these commands:

| Command | Vietnamese | Description |
|---------|------------|-------------|
| `exit` / `quit` | `thoát` | Exit the chat |
| `history` | `lịch sử` | Show recent conversation history |
| `stats` | `thống kê` | Show memory and session statistics |
| `clear` | `xóa` | Clear session memory |
| `context` | `ngữ cảnh` | Show current context for your question |

## 🔧 Configuration

### Environment Variables
```bash
# Required: CubeJS Configuration
export CUBEJS_API_URL="http://localhost:4000"
export CUBEJS_API_TOKEN="your-token"  # Optional

# Optional: Enhanced Memory (Golett AI)
export POSTGRES_CONNECTION="postgresql://user:pass@host:port/db"
export QDRANT_URL="http://localhost:6333"

# Optional: User Configuration
export USER_ID="your-user-id"
```

### Memory Backends

#### 🗂️ Local Storage (Default)
- Uses local files for memory storage
- Good for development and testing
- No external dependencies

#### 🤖 Golett AI Integration (Enhanced)
- Uses PostgreSQL + Qdrant for advanced memory
- Cross-session memory persistence
- Vector-based similarity search
- Enterprise-grade memory management

## 📊 Available Data Cubes

The chatbot can answer questions about:

### 💰 Sales Metrics (`sales_metrics`)
- **Measures**: `total_revenue`, `total_orders`, `new_customers`
- **Dimensions**: `date`, `region`
- **Example Questions**:
  - "Doanh thu tháng này như thế nào?"
  - "Có bao nhiêu đơn hàng mới?"
  - "Khách hàng mới theo khu vực?"

### 🏦 Financial Metrics (`financial_metrics`)
- **Measures**: `bank_inflow`, `bank_outflow`, `cash_balance`
- **Dimensions**: `date`, `account_type`
- **Example Questions**:
  - "Dòng tiền vào ngân hàng hôm nay?"
  - "Chi phí tài chính tháng này?"
  - "Số dư tài khoản hiện tại?"

### 🏭 Production Metrics (`production_metrics`)
- **Measures**: `raw_material_volume`, `finished_product_volume`
- **Dimensions**: `date`, `product_type`
- **Example Questions**:
  - "Sản lượng nguyên liệu thô?"
  - "Sản phẩm hoàn thành hôm nay?"
  - "Hiệu suất sản xuất theo loại?"

### 🏢 Companies (`companies`)
- **Measures**: `count`
- **Dimensions**: `company_name`, `company_code`, `industry`
- **Example Questions**:
  - "Có bao nhiêu công ty trong hệ thống?"
  - "Danh sách công ty theo ngành?"
  - "Công ty nào mới nhất?"

## 🎯 Context Awareness Examples

### **Building Context Over Time**
```
[1] User: "Doanh thu tháng này như thế nào?"
    🧠 Context: No previous context
    💡 Answer: [Gets sales data and stores in memory]

[2] User: "So với tháng trước thế nào?"
    🧠 Context: Previously discussed sales_metrics, total_revenue
    💡 Answer: [Compares with previous month, references past conversation]

[3] User: "Chi phí có tăng không?"
    🧠 Context: Discussing financial performance, previous sales context
    💡 Answer: [Gets financial data, relates to sales discussion]
```

### **Smart Suggestions**
After every 3 questions, the chatbot suggests related questions based on your conversation context:

```
💡 Gợi ý câu hỏi liên quan:
   1. Doanh thu so với tháng trước thế nào?
   2. Khách hàng mới tháng này bao nhiêu?
   3. Đơn hàng theo khu vực ra sao?
```

## 🔍 Memory Statistics

Use the `stats` command to see:
- **Session Statistics**: Questions asked, topics discussed
- **User Profile**: Favorite topics, total conversations
- **Memory Backend**: Which storage system is being used
- **Context Summary**: Recent conversation themes

## 🛠️ Troubleshooting

### Common Issues

#### ❌ "Cannot start chat without CubeJS connection"
**Solution**: Make sure CubeJS is running on the specified URL
```bash
# Check if CubeJS is running
curl http://localhost:4000/cubejs-api/v1/meta
```

#### ❌ "Memory backend: Unknown"
**Solution**: This is normal for local storage. For Golett integration, check PostgreSQL connection.

#### ❌ Tool execution errors
**Solution**: Verify your CubeJS schema matches the expected cube names and fields.

### Debug Mode
For detailed logging, set environment variable:
```bash
export LOG_LEVEL=DEBUG
```

## 🎉 Example Chat Session

```
🇻🇳 Vietnamese Business Intelligence Chatbot
============================================================
📱 Session ID: session_1201_1430
👤 User ID: vietnamese_user
📡 ✅ Kết nối thành công! Đã tải 4 cubes
🧠 Memory Backend: Local Files

💬 Chat Started! Type your questions in Vietnamese
============================================================

[1] 🤔 Câu hỏi của bạn: Doanh thu tháng này như thế nào?

🤖 Đang xử lý câu hỏi...
----------------------------------------

💡 **Trả lời:**
Doanh thu tháng này đạt 2.5 tỷ VND, tăng 15% so với tháng trước...

[2] 🤔 Câu hỏi của bạn: Chi phí có tăng không?

🤖 Đang xử lý câu hỏi...
----------------------------------------
🧠 Context: Đã thảo luận về sales_metrics

💡 **Trả lời:**
Chi phí tài chính tháng này là 800 triệu VND...

[3] 🤔 Câu hỏi của bạn: stats

📊 **Thống kê bộ nhớ:**
----------------------------------------
🔧 Memory Backend: Local Files
💬 Tổng câu hỏi session: 2
📋 Chủ đề đã thảo luận:
   - sales_metrics: 1 lần
   - financial_metrics: 1 lần
```

## 🚀 Advanced Usage

### Custom Session ID
```python
from chatbot_vietnamese.core.vietnamese_chatbot import VietnameseCubeJSChatbot

chatbot = VietnameseCubeJSChatbot(
    session_id="my_custom_session",
    user_id="my_user_id"
)
chatbot.start_interactive_chat()
```

### Programmatic Usage
```python
# Single question
answer = chatbot.ask("Doanh thu tháng này?")

# Get memory context
context = chatbot.memory_manager.get_memory_context("Tài chính?")

# Get conversation history
history = chatbot.get_conversation_history(limit=10)
```

---

**🎯 Ready to start?** Run the chatbot and begin asking your business questions in Vietnamese! 