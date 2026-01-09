import asyncio
import json
import os
from typing import AsyncGenerator
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from pathlib import Path

from src.agent.plan import PlanAgent
from src.inference.vertex_ai import ChatVertexAI

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
service_account_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "./service-account.json")
vertex_ai_model = os.environ.get("VERTEX_AI_MODEL", "gemini-1.5-flash")
vertex_ai_location = os.environ.get("VERTEX_AI_LOCATION", "us-central1")

llm = ChatVertexAI(
    model=vertex_ai_model,
    project_id=project_id,
    location=vertex_ai_location,
    temperature=0,
    service_account_path=service_account_path
)

class ChatRequest(BaseModel):
    message: str

# Global storage for interactive questions/answers
active_sessions = {}

class InteractiveAgent:
    def __init__(self, session_id, event_queue, loop):
        self.session_id = session_id
        self.event_queue = event_queue
        self.loop = loop
        self.answer_event = None
        self.user_answer = None
        
    def ask_user(self, question):
        """Send question to UI and wait for answer (blocking)"""
        import threading
        # Send question to UI
        self.loop.call_soon_threadsafe(
            lambda: self.event_queue.put_nowait({"type": "question", "content": question})
        )
        
        # Wait for answer using threading.Event
        self.answer_event = threading.Event()
        self.answer_event.wait()  # Block until answer is received
        return self.user_answer
        
    def provide_answer(self, answer):
        """Receive answer from UI"""
        self.user_answer = answer
        if self.answer_event:
            self.answer_event.set()

async def run_agent(input_text: str, event_queue: asyncio.Queue, session_id: str):
    loop = asyncio.get_running_loop()
    interactive_agent = InteractiveAgent(session_id, event_queue, loop)
    active_sessions[session_id] = interactive_agent
    
    def reporter(message, event_type="info", **kwargs):
        loop.call_soon_threadsafe(
            lambda: event_queue.put_nowait({"type": event_type, "content": message, **kwargs})
        )

    agent = PlanAgent(llm=llm, verbose=True, reporter=reporter, interactive_agent=interactive_agent)
    
    try:
        # Run in thread since invoke is blocking
        response = await asyncio.to_thread(agent.invoke, input_text)
        
        # Stream answer word by word
        await event_queue.put({"type": "answer_start", "content": ""})
        words = response.split()
        for i, word in enumerate(words):
            await event_queue.put({"type": "answer_chunk", "content": word + (" " if i < len(words) - 1 else "")})
            await asyncio.sleep(0.05)  # Small delay for streaming effect
        await event_queue.put({"type": "answer_end", "content": response})
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        await event_queue.put({"type": "error", "content": str(e)})
    finally:
        await event_queue.put({"type": "done", "content": ""})

@app.post("/chat")
async def chat(request: ChatRequest):
    # For simple curl testing
    agent = PlanAgent(llm=llm, verbose=True)
    response = agent.invoke(request.message)
    return {"response": response}

@app.get("/stream")
async def stream_chat(message: str):
    import uuid
    session_id = str(uuid.uuid4())
    event_queue = asyncio.Queue()
    
    # We need to run the agent in a separate thread because it's blocking
    async def event_generator():
        # Start agent task
        task = asyncio.create_task(run_agent(message, event_queue, session_id))
        
        while True:
            event = await event_queue.get()
            event["session_id"] = session_id
            yield f"data: {json.dumps(event)}\n\n"
            if event["type"] == "done":
                # Clean up session
                if session_id in active_sessions:
                    del active_sessions[session_id]
                break
        
        await task

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/answer")
async def submit_answer(request: dict):
    """Endpoint to receive user's answer to agent's question"""
    session_id = request.get("session_id")
    answer = request.get("answer")
    
    if session_id in active_sessions:
        active_sessions[session_id].provide_answer(answer)
        return {"status": "success"}
    return {"status": "error", "message": "Session not found"}

@app.get("/download/{filename}")
async def download_file(filename: str):
    """Download generated files"""
    # Check in current directory and common output directories
    possible_paths = [
        Path(filename),
        Path("output") / filename,
        Path("results") / filename,
        Path("data") / filename,
    ]
    
    for file_path in possible_paths:
        if file_path.exists() and file_path.is_file():
            return FileResponse(
                path=str(file_path),
                filename=filename,
                media_type="application/octet-stream"
            )
    
    raise HTTPException(status_code=404, detail="File not found")

# Mount static files
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
