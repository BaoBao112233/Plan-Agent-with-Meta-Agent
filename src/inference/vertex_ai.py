import anthropic
from typing import Optional, List, Union
import json
import os
from google.auth import default
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
import requests

from src.message import AIMessage, BaseMessage, HumanMessage, SystemMessage
from src.inference import BaseInference


class ChatVertexAI(BaseInference):
    """Wrapper for Google Vertex AI Gemini models using Claude SDK compatible interface"""
    
    def __init__(
        self,
        model: str = "gemini-1.5-flash",
        project_id: Optional[str] = None,
        location: str = "us-central1",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        service_account_path: Optional[str] = None,
    ):
        """
        Initialize Vertex AI Chat client
        
        Args:
            model: Model ID (e.g., 'gemini-1.5-flash')
            project_id: Google Cloud project ID
            location: Cloud location
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            service_account_path: Path to service account JSON file
        """
        super().__init__(model=model, temperature=temperature)
        self.project_id = project_id or os.environ.get("GOOGLE_CLOUD_PROJECT")
        self.location = location
        self.max_tokens = max_tokens
        
        # Initialize credentials
        if service_account_path:
            self.credentials = Credentials.from_service_account_file(
                service_account_path,
                scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )
        else:
            self.credentials, _ = default(
                scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )
        
        # Refresh credentials if needed
        if hasattr(self.credentials, 'refresh'):
            self.credentials.refresh(Request())
        
        # Initialize Anthropic client with Vertex AI endpoint
        self.client = anthropic.Anthropic(
            api_key="dummy",  # Required but not used for Vertex AI
            base_url=f"https://{self.location}-aiplatform.googleapis.com/v1beta1/projects/{self.project_id}/locations/{self.location}/endpoints/openapi",
        )
    
    def invoke(self, messages: Union[str, List[BaseMessage]], json: bool = False, **kwargs) -> AIMessage:
        """
        Send a message or list of messages to the model and get a response
        
        Args:
            messages: The prompt text or list of BaseMessage objects
            json: Whether to expect and parse JSON response
            **kwargs: Additional parameters
            
        Returns:
            AIMessage object
        """
        if isinstance(messages, str):
            messages = [HumanMessage(content=messages)]

        try:
            # Use the Vertex AI API directly with proper endpoint
            # Get access token from credentials
            access_token = self.credentials.token
            if not access_token:
                self.credentials.refresh(Request())
                access_token = self.credentials.token
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }
            
            # Prepare the request body for Vertex AI API
            url = f"https://{self.location}-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/publishers/google/models/{self.model}:generateContent"
            
            contents = []
            system_instruction = None
            
            for msg in messages:
                if isinstance(msg, SystemMessage):
                    system_instruction = {
                        "parts": [{"text": msg.content}]
                    }
                elif isinstance(msg, HumanMessage):
                    contents.append({
                        "role": "user",
                        "parts": [{"text": msg.content}]
                    })
                elif isinstance(msg, AIMessage):
                    contents.append({
                        "role": "model",
                        "parts": [{"text": msg.content}]
                    })
                elif isinstance(msg, dict):
                    role = msg.get("role", "user")
                    if role == "system":
                        system_instruction = {"parts": [{"text": msg.get("content", "")}]}
                    else:
                        contents.append({
                            "role": "model" if role == "assistant" else "user",
                            "parts": [{"text": msg.get("content", "")}]
                        })
            
            payload = {
                "contents": contents,
                "generationConfig": {
                    "temperature": self.temperature,
                    "maxOutputTokens": self.max_tokens,
                }
            }
            
            if system_instruction:
                payload["systemInstruction"] = system_instruction
                
            if json:
                payload["generationConfig"]["response_mime_type"] = "application/json"
            
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            
            # Extract text from response
            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    parts = candidate["content"]["parts"]
                    if len(parts) > 0 and "text" in parts[0]:
                        text = parts[0]["text"]
                        if json:
                            try:
                                import json as std_json
                                content = std_json.loads(text)
                                return AIMessage(content)
                            except std_json.JSONDecodeError:
                                pass
                        return AIMessage(text)
            
            return AIMessage("No response from model")
            
        except Exception as e:
            raise RuntimeError(f"Error calling Vertex AI API: {str(e)}")
    
    def __call__(self, messages: Union[str, List[BaseMessage]], **kwargs) -> AIMessage:
        """Allow object to be called directly"""
        return self.invoke(messages, **kwargs)
