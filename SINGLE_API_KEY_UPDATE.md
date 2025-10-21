# Cập nhật hệ thống từ Multiple API keys sang Single API key

## Tóm tắt thay đổi

Đã sửa lại toàn bộ repo để chỉ sử dụng 1 API key của Groq thay vì hệ thống multiple API keys phức tạp trước đây.

## Các file đã sửa

### 1. src/inference/__init__.py
- **Trước**: Hỗ trợ multiple API keys với logic rotation phức tạp
- **Sau**: Chỉ sử dụng 1 API key từ environment variable `GROQ_API_KEY`
- **Thay đổi**:
  - Loại bỏ `api_keys` list và `current_key_index`
  - Loại bỏ method `rotate_api_key()`
  - Đơn giản hóa constructor để chỉ sử dụng `self.api_key`

### 2. src/inference/groq.py
- **Trước**: Logic phức tạp với API key rotation, rate limiting, và failover
- **Sau**: Đơn giản với 1 API key và xử lý lỗi cơ bản
- **Thay đổi**:
  - Loại bỏ toàn bộ logic rotation trong `ChatGroq.invoke()`
  - Loại bỏ các method `_rotate_to_available_key()`, `_is_rate_limit_error()`, `_make_request()`
  - Đơn giản hóa xử lý lỗi trong cả `ChatGroq` và `AudioGroq`
  - Sử dụng `@retry` decorator cho reliability

### 3. app_production.py
- **Trước**: Hiển thị số lượng API keys được load
- **Sau**: Hiển thị thông báo sử dụng single API key
- **Thay đổi**: `print(f"🔑 Using single API key from environment")`

### 4. api/services.py
- **Trước**: Hiển thị số lượng API keys trong health check
- **Sau**: Hiển thị "configured (single key)"
- **Thay đổi**: Cập nhật health status message

### 5. Documentation (docs/)
- **Trước**: Ví dụ code với explicit API key parameter
- **Sau**: API key tự động load từ environment
- **Thay đổi**:
  - `docs/API_INTEGRATION.md`: Loại bỏ explicit api_key parameter
  - `docs/MCP_INTEGRATION.md`: Cập nhật ví dụ ChatGroq initialization

## Cấu hình

### Environment Variable
Chỉ cần 1 biến môi trường:
```bash
GROQ_API_KEY=your_groq_api_key_here
```

### Usage
```python
from src.inference.groq import ChatGroq

# API key tự động load từ environment
llm = ChatGroq('llama-3.3-70b-versatile', temperature=0)

# Hoặc truyền explicit
llm = ChatGroq('llama-3.3-70b-versatile', api_key='your_key', temperature=0)
```

## Lợi ích

1. **Đơn giản hóa**: Loại bỏ logic phức tạp không cần thiết
2. **Dễ maintain**: Ít code, ít bug potential
3. **Rõ ràng**: Dễ hiểu và debug
4. **Vẫn reliable**: Giữ retry logic cho network issues

## Files không thay đổi

- `app.py`: Đã sử dụng `ChatGroq()` mà không explicit API key
- Tất cả agent classes: Không sử dụng trực tiếp API key
- Notebooks: Không tìm thấy usage patterns cần sửa

## Kiểm tra

Đã test thành công:
```bash
python -c "from src.inference.groq import ChatGroq; llm = ChatGroq(); print(f'API key loaded: {llm.api_key[:10]}...' if llm.api_key else 'No API key found')"
# Output: API key loaded: gsk_lKa0Va...
```

Hệ thống đã sẵn sàng sử dụng với 1 API key duy nhất!