import os
import json
import aiohttp
import asyncio
from typing import List, Dict, Optional
from dotenv import load_dotenv

class GroqService:
    _instance = None
    
    def __init__(self):
        # Load environment variables
        load_dotenv()
        self.api_key = os.getenv('GROQ_API_KEY')
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
            
        self.base_url = 'https://api.groq.com/openai/v1/chat/completions'
        self.current_config = {
            "model": "mixtral-8x7b-32768",
            "temperature": 1,
            "max_tokens": 1024,
            "stream": False  # Changed to False for simpler response handling
        }

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def set_config(self, config: dict):
        self.current_config.update(config)

    def get_config(self):
        return self.current_config.copy()

    async def generate_response(self, messages: List[Dict]):
        try:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }
            
            payload = {
                **self.current_config,
                'messages': messages
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(self.base_url, headers=headers, json=payload) as response:
                    if not response.ok:
                        error_text = await response.text()
                        raise Exception(f"HTTP error! status: {response.status}, body: {error_text}")

                    json_response = await response.json()
                    return json_response['choices'][0]['message']

        except Exception as e:
            print(f'Error in generate_response: {e}')
            raise

    def extract_json_from_response(self, result: str) -> str:
        try:
            start_idx = result.find('{')
            end_idx = result.rfind('}') + 1
            if start_idx >= 0 and end_idx > 0:
                json_str = result[start_idx:end_idx]
                json_str = (json_str
                    .replace('\\n', '')
                    .replace('\\"', '"')
                    .replace('\\', '')
                    .replace('"{', '{')
                    .replace('}"', '}'))
                return json_str
            return result
        except Exception as e:
            print(f'Error extracting JSON: {e}')
            return result

# Example usage
async def main():
    groq_service = GroqService.get_instance()
    messages = [
        {"role": "user", "content": "Hello, how are you?"}
    ]
    response = await groq_service.generate_response(messages)
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
