# Chatbot Nông Nghiệp Tiếng Việt

Chatbot thông minh cho phân tích dữ liệu kinh doanh nông nghiệp, sử dụng Golett framework và CubeJS REST API.

## 🌟 Tính Năng

- **Hỗ trợ tiếng Việt**: Giao tiếp hoàn toàn bằng tiếng Việt
- **Phân tích dữ liệu thông minh**: Tự động chuyển đổi câu hỏi thành truy vấn CubeJS
- **Cơ sở tri thức**: Tích hợp kiến thức lĩnh vực nông nghiệp Việt Nam
- **Bộ nhớ hội thoại**: Ghi nhớ ngữ cảnh cuộc trò chuyện
- **Đa lĩnh vực**: Hỗ trợ tài chính, bán hàng, sản xuất, nhân sự, v.v.

## 🏗️ Kiến Trúc

```
chatbot_vietnamese/
├── __init__.py              # Package initialization
├── farm_chatbot.py          # Main chatbot class
├── query_mapper.py          # Vietnamese to CubeJS query mapping
├── knowledge_base.py        # Domain knowledge management
├── demo.py                  # Demo script
└── README.md               # Documentation
```

## 📋 Yêu Cầu

- Python 3.8+
- Golett framework
- CubeJS server đang chạy
- Các dependencies trong `requirements.txt`

## 🚀 Cài Đặt

1. **Clone repository và cài đặt dependencies:**
```bash
pip install -r requirements.txt
```

2. **Cấu hình biến môi trường:**
```bash
export CUBEJS_API_TOKEN="your_cubejs_token"
export CUBEJS_API_URL="http://localhost:4000/cubejs-api/v1"
```

3. **Đảm bảo CubeJS server đang chạy:**
```bash
# Trong thư mục cubejs/
npm start
```

## 💻 Sử Dụng

### Sử Dụng Cơ Bản

```python
from chatbot_vietnamese import FarmVietnameseChatbot

# Khởi tạo chatbot
chatbot = FarmVietnameseChatbot(
    cubejs_api_url="http://localhost:4000/cubejs-api/v1",
    cubejs_api_token="your_token",
    knowledge_file_path="farm_data/farm_business_domain_knowledge_vietnamese.md"
)

# Bắt đầu phiên chat
session_id = chatbot.start_session()

# Gửi câu hỏi
response = chatbot.chat("Doanh thu tháng này như thế nào?")
print(response)

# Kết thúc phiên
chatbot.end_session()
```

### Demo Script

```bash
cd chatbot_vietnamese
python demo.py
```

## 🗣️ Ví Dụ Câu Hỏi

### Tài Chính & Kế Toán
- "Doanh thu tháng này như thế nào?"
- "Chi phí năng lượng tuần trước là bao nhiêu?"
- "Số dư ngân hàng hiện tại?"
- "Tỷ lệ nợ của công ty?"

### Bán Hàng
- "Số đơn hàng hôm nay?"
- "Khách hàng mới tháng này có bao nhiêu?"
- "Thị phần của chúng ta như thế nào?"
- "Tỷ lệ giữ chân khách hàng?"

### Sản Xuất
- "Hiệu suất sản xuất hôm nay?"
- "Tỷ lệ lỗi tuần này?"
- "Khối lượng nguyên liệu đã sử dụng?"
- "Số lượng lao động trực tiếp?"

### Nhân Sự
- "Tổng số nhân viên hiện tại?"
- "Số người được tuyển mới tháng này?"
- "Buổi đào tạo nào đã tổ chức?"
- "Tỷ lệ đi muộn như thế nào?"

## 🔧 Cấu Hình

### Cấu Hình Chatbot

```python
chatbot = FarmVietnameseChatbot(
    cubejs_api_url="http://localhost:4000/cubejs-api/v1",
    cubejs_api_token="your_token",
    knowledge_file_path="path/to/knowledge.md",
    memory_config={
        "memory_type": "local",
        "max_memory_size": 1000,
        "conversation_window": 10
    }
)
```

### Cấu Hình Agent

Agent được cấu hình để:
- Trả lời bằng tiếng Việt
- Chuyên về lĩnh vực nông nghiệp
- Sử dụng dữ liệu CubeJS
- Ghi nhớ ngữ cảnh hội thoại

## 📊 Ánh Xạ Dữ Liệu

### Cubes Được Hỗ Trợ

| Lĩnh Vực | Cube | Mô Tả |
|----------|------|-------|
| Bán hàng | `sales_metrics` | Doanh thu, đơn hàng, khách hàng |
| Tài chính | `financial_metrics` | Chi phí, dòng tiền, ngân hàng |
| Sản xuất | `production_metrics` | Hiệu suất, chất lượng, khối lượng |
| Nhân sự | `hr_metrics` | Nhân viên, tuyển dụng, đào tạo |
| Thu mua | `procurement_metrics` | Nhà cung cấp, đơn hàng |
| Pháp lý | `legal_metrics` | Hợp đồng, tuân thủ |
| R&D | `rnd_metrics` | Nghiên cứu, phát triển |

### Từ Khóa Thời Gian

- `hôm nay`, `hôm qua`
- `tuần này`, `tuần trước`
- `tháng này`, `tháng trước`
- `năm này`, `năm trước`
- `7 ngày`, `30 ngày`

## 🧠 Cơ Sở Tri Thức

Chatbot sử dụng file kiến thức lĩnh vực `farm_business_domain_knowledge_vietnamese.md` chứa:

- Cơ cấu tổ chức doanh nghiệp
- Thông tin các phòng ban
- Quy trình kinh doanh
- Danh mục sản phẩm
- Chỉ số hiệu suất

## 🔍 API Reference

### FarmVietnameseChatbot

#### Methods

- `start_session(session_id=None)`: Bắt đầu phiên chat
- `chat(message)`: Xử lý tin nhắn
- `end_session()`: Kết thúc phiên chat
- `get_available_metrics()`: Lấy danh sách chỉ số
- `get_department_info(department)`: Thông tin phòng ban
- `execute_direct_query(query)`: Truy vấn trực tiếp CubeJS

### CubeJSQueryMapper

#### Methods

- `parse_vietnamese_query(question)`: Chuyển đổi câu hỏi tiếng Việt
- `_identify_cube(question)`: Xác định cube
- `_identify_measures(question, cube)`: Xác định measures
- `_identify_time_dimensions(question)`: Xác định thời gian

### FarmKnowledgeBase

#### Methods

- `get_department_info(department)`: Thông tin phòng ban
- `get_metrics_info()`: Danh sách chỉ số
- `get_product_info()`: Thông tin sản phẩm
- `search_knowledge(query)`: Tìm kiếm tri thức

## 🐛 Xử Lý Lỗi

Chatbot xử lý các lỗi phổ biến:

- Kết nối CubeJS thất bại
- Câu hỏi không hiểu được
- Dữ liệu không tồn tại
- Lỗi phân tích truy vấn

## 📈 Mở Rộng

### Thêm Cube Mới

1. Cập nhật `cube_mapping` trong `query_mapper.py`
2. Thêm measures và dimensions tương ứng
3. Cập nhật knowledge base

### Thêm Ngôn Ngữ

1. Tạo mapper mới cho ngôn ngữ đó
2. Cập nhật agent config
3. Thêm knowledge base tương ứng

## 🤝 Đóng Góp

1. Fork repository
2. Tạo feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📄 License

MIT License - xem file LICENSE để biết chi tiết.

## 📞 Hỗ Trợ

- Issues: GitHub Issues
- Documentation: README.md
- Demo: `python demo.py`

---

**Lưu ý**: Đảm bảo CubeJS server đang chạy và có dữ liệu trước khi sử dụng chatbot. 