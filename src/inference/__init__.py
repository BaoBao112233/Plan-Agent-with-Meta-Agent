from abc import ABC,abstractmethod
from src.message import AIMessage
from dotenv import load_dotenv
from os import environ

# Load environment variables
load_dotenv()

class BaseInference(ABC):
    def __init__(self,model:str='',api_key:str='',base_url:str='',temperature:float=0.5):
        self.model=model or 'llama-3.1-8b-instant'  # Working model
        
        # Dual API key support
        if api_key:
            self.api_keys = [api_key]
        else:
            # Load both API keys from environment
            key1 = environ.get('GROQ_API_KEY_1', '')
            key2 = environ.get('GROQ_API_KEY_2', '')
            key3 = environ.get('GROQ_API_KEY_3', '')
            self.api_keys = [key for key in [key1, key2, key3] if key]
            
        self.current_key_index = 0
        self.api_key = self.api_keys[0] if self.api_keys else ''
        
        self.base_url=base_url
        self.temperature=temperature
        self.headers={'Content-Type': 'application/json'}
        
        # Debug API key loading
        if not self.api_keys:
            print(f"⚠️  Warning: No API keys loaded for {self.__class__.__name__}")
        else:
            print(f"✅ Loaded {len(self.api_keys)} API key(s): {self.api_key[:10]}...")
    
    def rotate_api_key(self):
        """Rotate to next API key when current one hits rate limit"""
        if len(self.api_keys) > 1:
            old_index = self.current_key_index
            self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
            self.api_key = self.api_keys[self.current_key_index]
            print(f"🔄 Rotated API key from #{old_index+1} to #{self.current_key_index+1}: {self.api_key[:10]}...")
            return True
        else:
            print("⚠️  No additional API keys available for rotation")
            return False
            
    @abstractmethod
    def invoke(self,messages:list[dict])->AIMessage:
        pass