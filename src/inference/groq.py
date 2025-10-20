from requests import RequestException,HTTPError,ConnectionError
from tenacity import retry,stop_after_attempt,retry_if_exception_type,wait_exponential
from src.message import AIMessage,BaseMessage
from src.inference import BaseInference
from typing import Generator
from httpx import Client
from json import loads
import time

class ChatGroq(BaseInference):
    _last_request_time = 0
    _request_count = 0
    _max_requests_per_minute = 25  # Conservative rate limit per key
    _failed_keys = set()  # Track keys that hit rate limits
    
    def invoke(self, messages: list[BaseMessage], json: bool = False) -> AIMessage:
        """Invoke with automatic API key rotation on 429 errors"""
        max_cycles = 3  # Allow up to 3 full cycles through all keys
        
        for cycle in range(max_cycles):
            # Try each key once per cycle
            for key_attempt in range(len(self.api_keys)):
                try:
                    return self._make_request(messages, json)
                except Exception as err:
                    if self._is_rate_limit_error(err):
                        print(f"🚫 Rate limit hit on API key #{self.current_key_index + 1}")
                        self._failed_keys.add(self.current_key_index)
                        
                        # Try to rotate to next key that hasn't failed yet
                        if self._rotate_to_available_key():
                            print(f"🔄 Trying with API key #{self.current_key_index + 1}")
                            continue
                        else:
                            # All keys in this cycle failed, break to next cycle
                            print(f"💤 All API keys exhausted in cycle {cycle + 1}, waiting 60s...")
                            time.sleep(60)
                            self._failed_keys.clear()
                            self.current_key_index = 0
                            self.api_key = self.api_keys[0]
                            break  # Break to start next cycle
                    else:
                        # Non-rate-limit error, re-raise immediately
                        print(f"❌ Non-rate-limit error on API key #{self.current_key_index + 1}: {type(err).__name__}: {err}")
                        raise
        
        raise Exception(f"All {len(self.api_keys)} API keys failed after {max_cycles} cycles with 60s waits. Please check API key validity or try again later.")
    
    def _rotate_to_available_key(self) -> bool:
        """Rotate to next available API key that hasn't failed in current cycle"""
        if len(self.api_keys) <= 1:
            return False
            
        # Try each key starting from next one
        for _ in range(len(self.api_keys) - 1):
            self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
            if self.current_key_index not in self._failed_keys:
                self.api_key = self.api_keys[self.current_key_index]
                return True
        
        # All keys have failed in this cycle
        return False
    
    def _is_rate_limit_error(self, error) -> bool:
        """Check if error is a rate limit (429) error"""
        return (hasattr(error, 'response') and 
                hasattr(error.response, 'status_code') and 
                error.response.status_code == 429) or "429" in str(error)
    
    def _make_request(self, messages: list[BaseMessage], json: bool = False) -> AIMessage:
        """Make single API request with current key"""
        # Rate limiting per key
        current_time = time.time()
        
        # Reset counter every minute
        if current_time - self._last_request_time > 60:
            self._request_count = 0
        
        # Wait if we've hit rate limit for current key
        if self._request_count >= self._max_requests_per_minute:
            wait_time = 60 - (current_time - self._last_request_time)
            if wait_time > 0:
                print(f"🚫 Key #{self.current_key_index + 1} rate limit reached, waiting {wait_time:.1f}s...")
                time.sleep(wait_time)
                self._request_count = 0
        
        # Small delay between requests
        time.sleep(1.5)  # 1.5 second delay
        self._request_count += 1
        self._last_request_time = time.time()
        
        # Update headers with current API key
        self.headers.update({'Authorization': f'Bearer {self.api_key}'})
        headers = self.headers
        temperature = self.temperature
        url = self.base_url or "https://api.groq.com/openai/v1/chat/completions"
        messages = [message.to_dict() for message in messages]
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": False,
        }
        if json:
            payload["response_format"] = {
                "type": "json_object"
            }
        
        try:
            with Client() as client:
                response = client.post(url=url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            json_object = response.json()
            
            if json_object.get('error'):
                raise Exception(json_object['error']['message'])
            
            if json:
                content = loads(json_object['choices'][0]['message']['content'])
            else:
                content = json_object['choices'][0]['message']['content']
            
            return AIMessage(content)
            
        except Exception as err:
            # Re-raise to let the main invoke method handle API key rotation
            raise
    
    @retry(stop=stop_after_attempt(3),retry=retry_if_exception_type(RequestException))
    def stream(self, messages: list[BaseMessage],json=False)->Generator[str,None,None]:
        self.headers.update({'Authorization': f'Bearer {self.api_key}'})
        headers=self.headers
        temperature=self.temperature
        url=self.base_url or "https://api.groq.com/openai/v1/chat/completions"
        messages=[message.to_dict() for message in messages]
        payload={
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream":True,
        }
        if json:
            payload["response_format"]={
                "type": "json_object"
            }
        try:
            with Client() as client:
                response=client.post(url=url,json=payload,headers=headers)
            response.raise_for_status()
            chunks=response.iter_lines(decode_unicode=True)
            for chunk in chunks:
                chunk=chunk.replace('data: ','')
                if chunk and chunk!='[DONE]':
                    delta=loads(chunk)['choices'][0]['delta']
                    yield delta.get('content','')
        except HTTPError as err:
            err_object=loads(err.response.text)
            print(f'\nError: {err_object["error"]["message"]}\nStatus Code: {err.response.status_code}')
        except ConnectionError as err:
            print(err)
        exit()
    
    def available_models(self):
        url='https://api.groq.com/openai/v1/models'
        self.headers.update({'Authorization': f'Bearer {self.api_key}'})
        headers=self.headers
        with Client() as client:
            response=client.get(url=url,headers=headers)
        response.raise_for_status()
        models=response.json()
        return [model['id'] for model in models['data'] if model['active']]
    
class AudioGroq(BaseInference):
    def invoke(self,file_path:str='', language:str='en', json:bool=False)->AIMessage:
        headers={'Authorization': f'Bearer {self.api_key}'}
        temperature=self.temperature
        url=self.base_url or "https://api.groq.com/openai/v1/audio/transcriptions"
        payload={
            "model": self.model,
            "temperature": temperature,
            "language": language
        }
        files={
            'file': self.read_audio(file_path)
        }
        if json:
            payload["response_format"]={
                "type": "json"
            }
        else:
            payload['response_format']={
                "type":"text"
            }
        try:
            with Client() as client:
                response=client.post(url=url,json=payload,files=files,headers=headers,timeout=None)
            json_object=response.json()
            if json_object.get('error'):
                raise Exception(json_object['error']['message'])
            if json:
                content=loads(json_object['text'])
            else:
                content=json_object['text']
            return AIMessage(content)
        except HTTPError as err:
            err_object=loads(err.response.text)
            print(f'\nError: {err_object["error"]["message"]}\nStatus Code: {err.response.status_code}')
        except ConnectionError as err:
            print(err)
        exit()
    
    def read_audio(self,file_path:str):
        with open(file_path,'rb') as f:
            audio_data=f.read()
        return audio_data
    
    def available_models(self):
        url='https://api.groq.com/openai/v1/models'
        self.headers.update({'Authorization': f'Bearer {self.api_key}'})
        headers=self.headers
        with Client() as client:
            response=client.get(url=url,headers=headers)
        response.raise_for_status()
        models=response.json()
        return [model['id'] for model in models['data'] if model['active']]
