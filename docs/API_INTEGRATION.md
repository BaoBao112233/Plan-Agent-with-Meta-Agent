# Plan Agent API Integration

## Tổng quan

Plan Agent đã được tích hợp với Planner API để tự động tạo và cập nhật plans, tasks thông qua REST API endpoints.

## Cấu hình

### 1. Environment Variables

Thêm các biến môi trường sau vào file `.env`:

```env
GROQ_API_KEY=your_groq_api_key_here
API_BASE_URL=http://localhost:8000
```

### 2. API Server Requirements

API server cần có các endpoints sau (theo Planner API format):

#### POST /api/v1/plans
Tạo plans mới với tasks:
```json
[
  {
    "session_id": 1,
    "title": "Plan Agent - Simple",
    "goal_text": "user query",
    "trigger": "SYSTEM",
    "priority": 1,
    "tasks": [
      {
        "order_no": 1,
        "title": "Task title",
        "description": "Task description",
        "max_retries": 2
      }
    ]
  }
]
```

#### PUT /api/v1/plans/{plan_id}
Cập nhật plan status:
```json
{
  "status": "created|in_progress|completed|failed",
  "goal_text": "Updated goal"
}
```

#### PUT /api/v1/tasks/{task_id}
Cập nhật task status:
```json
{
  "status": "pending|in_progress|completed|failed",
  "execution_result": "Task execution result"
}
```

#### GET /api/v1/plans
Lấy tất cả plans

#### GET /api/v1/plans/{plan_id}
Lấy thông tin plan cụ thể

## Sử dụng

### 1. Kích hoạt API Integration

```python
from src.agent.plan import PlanAgent
from src.inference.groq import ChatGroq

# Với API enabled (mặc định)
agent = PlanAgent(llm=llm, verbose=True, api_enabled=True)

# Tắt API
agent = PlanAgent(llm=llm, verbose=True, api_enabled=False)
```

### 2. Chạy Agent

```python
response = agent.invoke("Your query here")
```

## API Events Flow

1. **Plan Creation**: Tạo plan với tất cả tasks khi plan được tạo
2. **Execution Start**: Cập nhật plan status thành "in_progress"
3. **Task Execution**: 
   - Update task status thành "in_progress" khi bắt đầu
   - Update task status thành "completed" với execution result khi hoàn thành
4. **Plan Updates**: Theo dõi và cập nhật trạng thái pending/completed tasks
5. **Final Result**: Cập nhật plan status thành "completed" với final answer

## APIClient Methods

### Core Methods
- `create_plan(plan_data)`: Tạo plan mới với tasks
- `update_plan_status(status, goal_text)`: Cập nhật status của plan
- `update_task_status(task_title, status, execution_result)`: Cập nhật status của task
- `get_plan(plan_id)`: Lấy thông tin plan
- `get_all_plans()`: Lấy tất cả plans

### Backward Compatibility Methods
- `send_plan_status(plan_data)`: Compatibility wrapper
- `send_task_update(task_data)`: Compatibility wrapper  
- `send_final_result(result_data)`: Compatibility wrapper

## Testing

Chạy test script để kiểm tra API integration:

```bash
python test_api_integration.py
```

## Troubleshooting

### API Connection Issues

- Kiểm tra API server có đang chạy tại `http://localhost:8000`
- Kiểm tra endpoints có sẵn trong API server
- Kiểm tra network connectivity

### Debugging API Calls

API client sẽ in ra status messages với emoji indicators:
- ✅ Success operations
- ❌ Error operations  
- 🎉 Plan completion

### Tắt API Integration

Nếu không muốn sử dụng API integration:
```python
agent = PlanAgent(llm=llm, verbose=True, api_enabled=False)
```

## Example Usage

```python
from src.agent.plan import PlanAgent
from src.inference.groq import ChatGroq
from dotenv import load_dotenv
from os import environ

load_dotenv()

# Setup - API key is automatically loaded from environment
llm = ChatGroq('llama-3.3-70b-versatile', temperature=0)

# Create agent with API enabled
agent = PlanAgent(llm=llm, verbose=True, api_enabled=True)

# Execute query - will automatically create plan and update statuses via API
response = agent.invoke("Create a plan to organize my workspace")

print(f"Final Response: {response}")
```