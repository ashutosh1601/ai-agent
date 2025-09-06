from typing import Dict, Any
from ..utils.ollama_client import call_ollama


class InputRefinement:
    """Component for refining user input queries."""
    
    async def refine_user_input(self, user_input: str) -> Dict[str, Any]:
        """Refine user input to be more specific and clear for SQL generation."""
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
        
        try:
            response = await call_ollama(prompt)
            return {
                'original': user_input,
                'refined': response,
                'success': True
            }
        except Exception as error:
            return {
                'original': user_input,
                'refined': user_input,
                'success': False,
                'error': str(error)
            }