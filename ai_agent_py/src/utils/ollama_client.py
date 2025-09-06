import os
from typing import List, Optional
import ollama
from dotenv import load_dotenv

load_dotenv()


async def call_ollama(prompt: str, model: Optional[str] = None) -> str:
    """Call Ollama API with the given prompt and model."""
    try:
        client = ollama.AsyncClient(host=os.getenv('OLLAMA_HOST', 'http://localhost:11434'))
        
        response = await client.chat(
            model=model or os.getenv('OLLAMA_MODEL', 'llama3.1'),
            messages=[
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            options={
                'temperature': 0.1,
                'num_predict': 2000
            }
        )
        
        return response['message']['content']
    except Exception as error:
        print(f'Ollama API Error: {error}')
        raise Exception(f'Ollama API call failed: {str(error)}')


async def list_ollama_models() -> List[str]:
    """List available Ollama models."""
    try:
        client = ollama.AsyncClient(host=os.getenv('OLLAMA_HOST', 'http://localhost:11434'))
        models = await client.list()
        return [model['name'] for model in models['models']]
    except Exception as error:
        print(f'Error listing Ollama models: {error}')
        raise Exception(f'Failed to list Ollama models: {str(error)}')


async def check_ollama_connection() -> bool:
    """Check if Ollama connection is working."""
    try:
        client = ollama.AsyncClient(host=os.getenv('OLLAMA_HOST', 'http://localhost:11434'))
        await client.list()
        return True
    except Exception:
        return False