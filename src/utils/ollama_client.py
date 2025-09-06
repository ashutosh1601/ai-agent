import os
import logging
from typing import List, Optional
import ollama
from dotenv import load_dotenv

load_dotenv()

# Set up logger
logger = logging.getLogger(__name__)


async def call_ollama(prompt: str, model: Optional[str] = None) -> str:
    """Call Ollama API with the given prompt and model."""
    host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
    model_name = model or os.getenv('OLLAMA_MODEL', 'llama3.1')
    
    logger.info(f"Making Ollama API call to {host} with model {model_name}")
    logger.debug(f"Prompt length: {len(prompt)} characters")
    logger.debug(f"Prompt preview: {prompt[:200]}...")
    
    try:
        client = ollama.AsyncClient(host=host)
        
        logger.debug("Sending chat request to Ollama")
        response = await client.chat(
            model=model_name,
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
        
        response_content = response['message']['content']
        logger.info(f"Received response from Ollama (length: {len(response_content)} characters)")
        logger.debug(f"Response content: {response_content}")
        
        return response_content
        
    except Exception as error:
        logger.error(f"Ollama API call failed: {str(error)}")
        print(f'Ollama API Error: {error}')
        raise Exception(f'Ollama API call failed: {str(error)}')


async def list_ollama_models() -> List[str]:
    """List available Ollama models."""
    host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
    logger.info(f"Listing available Ollama models from {host}")
    
    try:
        client = ollama.AsyncClient(host=host)
        models = await client.list()
        model_names = [model['name'] for model in models['models']]
        logger.info(f"Found {len(model_names)} available models: {model_names}")
        return model_names
    except Exception as error:
        logger.error(f"Failed to list Ollama models: {str(error)}")
        print(f'Error listing Ollama models: {error}')
        raise Exception(f'Failed to list Ollama models: {str(error)}')


async def check_ollama_connection() -> bool:
    """Check if Ollama connection is working."""
    host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
    logger.info(f"Checking Ollama connection to {host}")
    
    try:
        client = ollama.AsyncClient(host=host)
        await client.list()
        logger.info("Ollama connection successful")
        return True
    except Exception as error:
        logger.warning(f"Ollama connection failed: {str(error)}")
        return False