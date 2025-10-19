# Plan Agent API Integration

## Tổng quan

Plan Agent đã được tích hợp với khả năng gửi thông tin plan status và task updates lên API server thông qua các endpoint REST API.

## Cấu hình

### 1. Environment Variables

Thêm các biến môi trường sau vào file `.env`:

```env
GROQ_API_KEY=your_groq_api_key_here
API_BASE_URL=http://localhost:8000
```

### 2. API Server Requirements

API server cần có các endpoints sau:

#### POST /plan/status
Nhận thông tin trạng thái plan:
```json
{
  "input": "user query",
  "plan_type": "simple|advanced|execution",
  "current_plan": ["task1", "task2", "task3"],
  "pending_tasks": ["task2", "task3"],
  "completed_tasks": ["task1"],
  "current_task": "task2",
  "status": "plan_created|execution_started|plan_updated",
  "timestamp": "2025-10-19T10:30:00"
}
```

#### POST /task/update
Nhận thông tin cập nhật task:
```json
{
  "task_name": "task description",
  "task_response": "response from task execution",
  "status": "task_completed",
  "timestamp": "2025-10-19T10:30:00"
}
```

#### POST /plan/result
Nhận kết quả cuối cùng:
```json
{
  "input": "user query",
  "final_answer": "final response",
  "completed_tasks": ["task1", "task2", "task3"],
  "execution_time": 45.6,
  "timestamp": "2025-10-19T10:30:00"
}
```

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

1. **Plan Creation**: Khi plan được tạo (simple/advanced)
2. **Execution Start**: Khi bắt đầu thực hiện plan
3. **Task Updates**: Mỗi khi hoàn thành một task
4. **Plan Updates**: Khi cập nhật trạng thái pending/completed tasks
5. **Final Result**: Khi hoàn thành toàn bộ plan

## Troubleshooting

### API Connection Issues
- Kiểm tra API server có đang chạy tại `http://localhost:8000`
- Kiểm tra endpoints có sẵn trong API server
- Kiểm tra network connectivity

### Debugging API Calls
API client sẽ in ra lỗi nếu không kết nối được với server, nhưng sẽ không dừng việc thực thi của Plan Agent.

### Tắt API Integration
Nếu không muốn sử dụng API integration:
```python
agent = PlanAgent(llm=llm, verbose=True, api_enabled=False)
```

## Example API Server

Bạn có thể tạo một simple API server bằng FastAPI:

```python
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

class PlanStatus(BaseModel):
    input: str
    plan_type: str
    current_plan: List[str]
    pending_tasks: List[str]
    completed_tasks: List[str]
    current_task: str
    status: str
    timestamp: str

class TaskUpdate(BaseModel):
    task_name: str
    task_response: str
    status: str
    timestamp: str

class PlanResult(BaseModel):
    input: str
    final_answer: str
    completed_tasks: List[str]
    execution_time: float
    timestamp: str

@app.post("/plan/status")
async def update_plan_status(status: PlanStatus):
    print(f"Plan Status: {status}")
    return {"message": "Plan status updated"}

@app.post("/task/update")
async def update_task(task: TaskUpdate):
    print(f"Task Update: {task}")
    return {"message": "Task updated"}

@app.post("/plan/result")
async def final_result(result: PlanResult):
    print(f"Final Result: {result}")
    return {"message": "Final result received"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

Chạy server:
```bash
pip install fastapi uvicorn
uvicorn main:app --reload
```