import logging
from typing import Dict, Any
from ..utils.ollama_client import call_ollama

# Set up logger
logger = logging.getLogger(__name__)


class InputRefinement:
    """Component for refining user input queries."""
    
    async def refine_user_input(self, user_input: str) -> Dict[str, Any]:
        """Refine user input to be more specific and clear for SQL generation."""
        logger.info(f"Starting input refinement for: '{user_input}'")
        
        prompt = f"""
You are an AI assistant that refines user queries for SQL generation. 
Your task is to take a user's natural language query and refine it to be more specific, clear, and suitable for SQL query generation.

User Input: "{user_input}"

Please refine this input by:
1. Clarifying any ambiguous terms
2. Adding specific details that would be helpful for SQL generation
3. Identifying the main intent (SELECT, UPDATE, DELETE, etc.)
4. Suggesting specific data types or ranges where appropriate

Return only the refined query in a clear, concise format.
"""
        
        logger.info("Sending prompt to Ollama API for input refinement")
        logger.debug(f"Full prompt (length: {len(prompt)} chars): {prompt[:300]}...")
        
        try:
            response = await call_ollama(prompt)
            logger.info(f"Received refinement response from Ollama (length: {len(response)} chars)")
            logger.info(f"Original input: '{user_input}' -> Refined: '{response.strip()}'")
            logger.debug(f"Full response: {response}")
            
            result = {
                'original': user_input,
                'refined': response.strip(),
                'success': True
            }
            
            logger.info("Input refinement completed successfully")
            logger.debug(f"Full refinement result: {result}")
            
            return result
            
        except Exception as error:
            logger.error(f"Input refinement failed: {str(error)}")
            logger.exception("Full exception details:")
            
            error_result = {
                'original': user_input,
                'refined': user_input,
                'success': False,
                'error': str(error)
            }
            
            logger.warning("Returning original input due to refinement failure")
            logger.debug(f"Returning error result: {error_result}")
            
            return error_result