import anthropic
from typing import Optional
import json
import os
from google.auth import default
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials


class ChatVertexAI:
    """Wrapper for Google Vertex AI Gemini models using Claude SDK compatible interface"""
    
    def __init__(
        self,
        model: str = "gemini-2.5-flash",
        project_id: Optional[str] = None,
        location: str = "us-central1",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        service_account_path: Optional[str] = None,
    ):
        """
        Initialize Vertex AI Chat client
        
        Args:
            model: Model ID (e.g., 'gemini-2.5-flash')
            project_id: Google Cloud project ID
            location: Cloud location
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            service_account_path: Path to service account JSON file
        """
        self.model = model
        self.project_id = project_id or os.environ.get("GOOGLE_CLOUD_PROJECT")
        self.location = location
        self.temperature = temperature
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
    
    def invoke(self, input_text: str, **kwargs) -> str:
        """
        Send a message to the model and get a response
        
        Args:
            input_text: The prompt text
            **kwargs: Additional parameters
            
        Returns:
            Model response text
        """
        try:
            # Use the Vertex AI API directly with proper endpoint
            import requests
            
            # Get access token from credentials
            access_token = self.credentials.token
            if not access_token or not hasattr(self.credentials, 'token'):
                self.credentials.refresh(Request())
                access_token = self.credentials.token
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }
            
            # Prepare the request body for Vertex AI API
            url = f"https://{self.location}-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/publishers/google/models/{self.model}:generateContent"
            
            payload = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [
                            {
                                "text": input_text
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": self.temperature,
                    "maxOutputTokens": self.max_tokens,
                }
            }
            
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            
            # Extract text from response
            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    parts = candidate["content"]["parts"]
                    if len(parts) > 0 and "text" in parts[0]:
                        return parts[0]["text"]
            
            return "No response from model"
            
        except Exception as e:
            raise RuntimeError(f"Error calling Vertex AI API: {str(e)}")
    
    def __call__(self, input_text: str, **kwargs) -> str:
        """Allow object to be called directly"""
        return self.invoke(input_text, **kwargs)
