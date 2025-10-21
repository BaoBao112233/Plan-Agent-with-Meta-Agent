from abc import ABC,abstractmethod
from src.message import AIMessage
from dotenv import load_dotenv
from os import environ

# Load environment variables
load_dotenv()

class BaseInference(ABC):
    def __init__(self,model:str='',api_key:str='',base_url:str='',temperature:float=0.5):
        self.model=model or 'llama-3.1-8b-instant'  # Working model
        
        # Single API key support
        if api_key:
            self.api_key = api_key
        else:
            # Load API key from environment
            self.api_key = environ.get('GROQ_API_KEY', '')
        
        self.base_url=base_url
        self.temperature=temperature
        self.headers={'Content-Type': 'application/json'}
            
    @abstractmethod
    def invoke(self,messages:list[dict])->AIMessage:
        pass