import json
import re
import logging
from typing import List, Dict, Any, Optional
from ..utils.ollama_client import call_ollama

# Set up logger
logger = logging.getLogger(__name__)


class QuerySelector:
    """Component for selecting the best matching example query."""
    
    def __init__(self, example_queries: List[Dict[str, str]] = None):
        self.example_queries = example_queries or []
        logger.info(f"QuerySelector initialized with {len(self.example_queries)} example queries")
    
    def add_example_query(self, query: str, description: str) -> None:
        """Add an example query with description."""
        logger.debug(f"Adding example query: {description}")
        self.example_queries.append({'query': query, 'description': description})
        logger.info(f"Total example queries: {len(self.example_queries)}")
    
    async def select_best_query(self, user_prompt: str) -> Dict[str, Any]:
        """Select the best matching example query for the user prompt."""
        logger.info(f"Starting query selection for prompt: '{user_prompt}'")
        
        if not self.example_queries:
            logger.warning("No example queries available for selection")
            return {
                'selected_query': None,
                'confidence': 0,
                'reasoning': "No example queries available"
            }
        
        logger.info(f"Analyzing {len(self.example_queries)} example queries")
        
        example_queries_text = '\n'.join([
            f"""
Example {index + 1}:
Description: {example['description']}
SQL Query: {example['query']}
"""
            for index, example in enumerate(self.example_queries)
        ])
        
        logger.debug(f"Generated example queries text (length: {len(example_queries_text)} chars)")
        logger.debug(f"Example queries preview: {example_queries_text[:300]}...")
        
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
        
        logger.info("Sending prompt to Ollama API for query selection")
        logger.debug(f"Full prompt (length: {len(prompt)} chars): {prompt[:300]}...")
        
        try:
            response = await call_ollama(prompt)
            logger.info(f"Received response from Ollama (length: {len(response)} chars)")
            logger.debug(f"Raw response: {response}")
            
            # Extract JSON from response (handle extra text before/after JSON)
            logger.info("Extracting JSON from response")
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if not json_match:
                logger.error("No JSON object found in response")
                raise ValueError("No JSON object found in response")
            
            json_str = json_match.group(0)
            logger.info(f"Extracted JSON string (length: {len(json_str)} chars)")
            logger.debug(f"JSON string: {json_str}")
            
            logger.info("Parsing JSON")
            result = json.loads(json_str)
            logger.info("JSON parsed successfully")
            logger.debug(f"Parsed result: {result}")
            
            # Validate required keys
            logger.info("Validating required keys")
            required_keys = ['selectedQueryIndex', 'selectedQuery', 'confidence', 'reasoning']
            missing_keys = [key for key in required_keys if key not in result]
            if missing_keys:
                logger.error(f"Missing required keys: {missing_keys}")
                raise ValueError(f"Missing required keys in response: {missing_keys}")
            
            logger.info("All required keys found in response")
            
            final_result = {
                'selected_query': result['selectedQuery'],
                'selected_query_index': result['selectedQueryIndex'],
                'confidence': result['confidence'],
                'reasoning': result['reasoning'],
                'success': True
            }
            
            logger.info(f"Query selection completed successfully. Selected query index: {result['selectedQueryIndex']}, confidence: {result['confidence']}%")
            logger.debug(f"Full result: {final_result}")
            
            return final_result
            
        except json.JSONDecodeError as json_error:
            logger.error(f"JSON parsing failed: {str(json_error)}")
            logger.error(f"Raw response that failed parsing: {response[:500]}...")
            error_result = {
                'selected_query': None,
                'confidence': 0,
                'reasoning': f"JSON parsing error: {str(json_error)}. Raw response: {response[:200]}...",
                'success': False,
                'error': f"JSON decode error: {str(json_error)}"
            }
            logger.debug(f"Returning error result: {error_result}")
            return error_result
            
        except Exception as error:
            logger.error(f"General error in query selection: {str(error)}")
            logger.exception("Full exception details:")
            error_result = {
                'selected_query': None,
                'confidence': 0,
                'reasoning': f"Error selecting query: {str(error)}",
                'success': False,
                'error': str(error)
            }
            logger.debug(f"Returning error result: {error_result}")
            return error_result