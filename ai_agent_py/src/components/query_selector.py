import json
from typing import List, Dict, Any, Optional
from ..utils.ollama_client import call_ollama


class QuerySelector:
    """Component for selecting the best matching example query."""
    
    def __init__(self, example_queries: List[Dict[str, str]] = None):
        self.example_queries = example_queries or []
    
    def add_example_query(self, query: str, description: str) -> None:
        """Add an example query with description."""
        self.example_queries.append({'query': query, 'description': description})
    
    async def select_best_query(self, user_prompt: str) -> Dict[str, Any]:
        """Select the best matching example query for the user prompt."""
        if not self.example_queries:
            return {
                'selected_query': None,
                'confidence': 0,
                'reasoning': "No example queries available"
            }
        
        example_queries_text = '\n'.join([
            f"""
Example {index + 1}:
Description: {example['description']}
SQL Query: {example['query']}
"""
            for index, example in enumerate(self.example_queries)
        ])
        
        prompt = f"""
You are an expert SQL analyst. Given a user's request and a set of example SQL queries, select the most appropriate example query that best matches the user's intent.

User Request: "{user_prompt}"

Available Example Queries:
{example_queries_text}

Please analyze the user request and:
1. Select the example query that best matches the user's intent
2. Provide a confidence score (0-100)
3. Explain your reasoning

Respond in JSON format:
{{
  "selectedQueryIndex": <index_of_selected_query>,
  "selectedQuery": "<the_selected_sql_query>",
  "confidence": <confidence_score>,
  "reasoning": "<explanation_of_why_this_query_was_selected>"
}}
"""
        
        try:
            response = await call_ollama(prompt)
            result = json.loads(response)
            
            return {
                'selected_query': result['selectedQuery'],
                'selected_query_index': result['selectedQueryIndex'],
                'confidence': result['confidence'],
                'reasoning': result['reasoning'],
                'success': True
            }
        except Exception as error:
            return {
                'selected_query': None,
                'confidence': 0,
                'reasoning': f"Error selecting query: {str(error)}",
                'success': False,
                'error': str(error)
            }