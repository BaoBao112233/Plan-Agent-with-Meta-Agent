# Setup Vertex AI with Gemini 2.5 Flash

Hướng dẫn cấu hình repo để sử dụng Google Vertex AI với model Gemini 2.5 Flash.

## Yêu cầu

1. **Tài khoản Google Cloud** với dự án đã được tạo
2. **Vertex AI API** đã được bật
3. **Service Account** được cấu hình

## Các bước setup

### 1. Cài đặt Dependencies

```bash
pip install -r requirements.txt
```

### 2. Tạo Service Account

#### Option A: Sử dụng Google Cloud Console

1. Truy cập [Google Cloud Console](https://console.cloud.google.com/)
2. Chọn dự án của bạn
3. Vào **Service Accounts** (IAM & Admin > Service Accounts)
4. Click **Create Service Account**
5. Đặt tên: `vertex-ai-agent`
6. Click **Create and Continue**
7. Grant roles:
   - `Vertex AI User`
   - `Vertex AI Service Agent`
   - `Service Account User`
8. Click **Continue** > **Done**
9. Vào service account vừa tạo
10. Tab **Keys** > **Add Key** > **Create new key**
11. Chọn **JSON** > **Create**
12. File JSON sẽ được tải về - lưu vào thư mục root project với tên `service-account.json`

#### Option B: Sử dụng gcloud CLI

```bash
# Set project
gcloud config set project YOUR_PROJECT_ID

# Create service account
gcloud iam service-accounts create vertex-ai-agent

# Grant roles
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:vertex-ai-agent@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

# Create and download key
gcloud iam service-accounts keys create service-account.json \
  --iam-account=vertex-ai-agent@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

### 3. Cấu hình Environment Variables

Tạo file `.env` từ `.env.example`:

```bash
cp .env.example .env
```

Chỉnh sửa `.env`:

```env
GOOGLE_CLOUD_PROJECT=your_project_id
GOOGLE_APPLICATION_CREDENTIALS=./service-account.json
VERTEX_AI_MODEL=gemini-2.5-flash
VERTEX_AI_LOCATION=us-central1
```

### 4. Kiểm tra Setup

```bash
python -c "from src.inference.vertex_ai import ChatVertexAI; print('✓ Vertex AI import successful')"
```

### 5. Chạy Ứng dụng

```bash
python app.py
```

## Troubleshooting

### Lỗi: "GOOGLE_CLOUD_PROJECT not found"

- Kiểm tra file `.env` đã được tạo
- Đảm bảo `GOOGLE_CLOUD_PROJECT` có giá trị chính xác

### Lỗi: "service-account.json not found"

- Đảm bảo file `service-account.json` nằm ở thư mục root
- Hoặc cập nhật `GOOGLE_APPLICATION_CREDENTIALS` trong `.env` với đường dẫn chính xác

### Lỗi: "Permission denied"

- Kiểm tra service account có các roles cần thiết
- Đảm bảo Vertex AI API đã được bật trong Google Cloud Console

### Lỗi: "Model not found"

- Kiểm tra model `gemini-2.5-flash` có sẵn tại location được chỉ định
- Thử các vị trí khác: `us-central1`, `us-west1`, `europe-west1`

## Sử dụng ChatVertexAI trong Code

```python
from src.inference.vertex_ai import ChatVertexAI
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatVertexAI(
    model="gemini-2.5-flash",
    project_id=os.environ.get("GOOGLE_CLOUD_PROJECT"),
    location="us-central1",
    temperature=0.7,
    service_account_path="./service-account.json"
)

response = llm.invoke("Hello, how are you?")
print(response)
```

## Giới hạn & Lưu ý

- **Rate Limiting**: Vertex AI có giới hạn request/phút
- **Chi phí**: Vertex AI là dịch vụ trả phí theo lượng token sử dụng
- **Model Updates**: Kiểm tra [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs) để cập nhật tên model mới

## Liên kết hữu ích

- [Vertex AI Quickstart](https://cloud.google.com/vertex-ai/docs/start/quickstarts/api-quickstart)
- [Gemini API Reference](https://cloud.google.com/vertex-ai/docs/generative-ai/model-reference/gemini)
- [Service Account Documentation](https://cloud.google.com/iam/docs/service-accounts)
