import requests
import json
from typing import List, Dict, Optional
from os import environ
from dotenv import load_dotenv

load_dotenv()

class APIClient:
    """Client để gửi thông tin plan và task status lên API server"""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or environ.get("API_BASE_URL", "http://localhost:8000")
        self.session = requests.Session()
        # Có thể thêm authentication headers nếu cần
        # self.session.headers.update({"Authorization": f"Bearer {api_token}"})
    
    def send_plan_status(self, plan_data: Dict) -> Optional[Dict]:
        """
        Gửi thông tin plan status lên API server
        
        Args:
            plan_data: Dictionary chứa thông tin plan
            {
                "input": str,
                "plan_type": str,
                "current_plan": List[str],
                "pending_tasks": List[str],
                "completed_tasks": List[str],
                "current_task": str,
                "status": str
            }
        """
        try:
            response = self.session.post(
                f"{self.base_url}/plan/status",
                json=plan_data,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error sending plan status to API: {e}")
            return None
    
    def send_task_update(self, task_data: Dict) -> Optional[Dict]:
        """
        Gửi thông tin task update lên API server
        
        Args:
            task_data: Dictionary chứa thông tin task
            {
                "task_name": str,
                "task_response": str,
                "status": str,
                "timestamp": str
            }
        """
        try:
            response = self.session.post(
                f"{self.base_url}/task/update",
                json=task_data,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error sending task update to API: {e}")
            return None
    
    def send_final_result(self, result_data: Dict) -> Optional[Dict]:
        """
        Gửi kết quả final lên API server
        
        Args:
            result_data: Dictionary chứa kết quả final
            {
                "input": str,
                "final_answer": str,
                "completed_tasks": List[str],
                "execution_time": float
            }
        """
        try:
            response = self.session.post(
                f"{self.base_url}/plan/result",
                json=result_data,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error sending final result to API: {e}")
            return None