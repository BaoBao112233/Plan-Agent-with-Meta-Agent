"""
📖 FastAPI Server Startup Script
================================

Simple script to run the Plan Agent FastAPI server
"""

import os
import sys

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting Plan Agent FastAPI Server")
    print("📊 Health check: http://localhost:8000/health")
    print("📚 Documentation: http://localhost:8000/docs")
    print("🔄 WebSocket: ws://localhost:8000/ws/{client_id}")
    print("=" * 50)
    
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=9000,
        reload=True,
        log_level="info"
    )