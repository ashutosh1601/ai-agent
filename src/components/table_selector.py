import json
import re
import logging
from typing import Dict, Any, List
from ..utils.ollama_client import call_ollama

# Set up logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class TableSelector:
    """Component for selecting relevant tables and columns."""
    
    def __init__(self, table_metadata: Dict[str, Any] = None):
        self.table_metadata = table_metadata or {}
    
    def add_table_metadata(self, table_name: str, metadata: Dict[str, Any]) -> None:
        """Add metadata for a table."""
        self.table_metadata[table_name] = metadata
    
    async def select_tables_and_columns(self, user_prompt: str) -> Dict[str, Any]:
        """Select relevant tables and columns for the user prompt."""
        logger.info(f"Starting table selection for prompt: '{user_prompt}'")
        
        if not self.table_metadata:
            logger.warning("No table metadata available")
            return {
                'selected_tables': [],
                'selected_columns': {},
                'reasoning': "No table metadata available"
            }
        
        logger.info(f"Processing metadata for {len(self.table_metadata)} tables: {list(self.table_metadata.keys())}")
        
        metadata_text = '\n'.join([
            f"""
Table: {table_name}
Description: {metadata.get('description', 'No description available')}
Columns:
{chr(10).join([f"  - {col['name']} ({col['type']}): {col.get('description', 'No description')}" for col in metadata['columns']])}
"""
            for table_name, metadata in self.table_metadata.items()
        ])
        
        logger.debug(f"Generated metadata text (length: {len(metadata_text)} chars)")
        logger.debug(f"Metadata preview: {metadata_text[:200]}...")
        
        prompt = f"""
You are a database expert. Given a user's request and database table metadata, identify the most relevant tables and columns needed to fulfill the request.

User Request: "{user_prompt}"

Available Tables and Columns:
{metadata_text}

Please analyze the user request and:
1. Identify which tables are needed
2. Identify which specific columns from each table are required
3. Explain your reasoning

Respond in JSON format:
{{
  "selectedTables": ["table1", "table2"],
  "selectedColumns": {{
    "table1": ["column1", "column2"],
    "table2": ["column3", "column4"]
  }},
  "reasoning": "<explanation_of_selections>",
  "confidence": <confidence_score_0_to_100>
}}
"""
        
        logger.info("Sending prompt to Ollama API")
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
            required_keys = ['selectedTables', 'selectedColumns', 'reasoning', 'confidence']
            missing_keys = [key for key in required_keys if key not in result]
            if missing_keys:
                logger.error(f"Missing required keys: {missing_keys}")
                raise ValueError(f"Missing required keys in response: {missing_keys}")
            
            logger.info("All required keys found in response")
            
            final_result = {
                'selected_tables': result['selectedTables'],
                'selected_columns': result['selectedColumns'],
                'reasoning': result['reasoning'],
                'confidence': result['confidence'],
                'success': True
            }
            
            logger.info(f"Successfully processed table selection. Selected {len(final_result['selected_tables'])} tables")
            logger.info(f"Selected tables: {final_result['selected_tables']}")
            logger.info(f"Confidence score: {final_result['confidence']}")
            logger.debug(f"Full result: {final_result}")
            
            return final_result
            
        except json.JSONDecodeError as json_error:
            logger.error(f"JSON parsing failed: {str(json_error)}")
            logger.error(f"Raw response that failed parsing: {response[:500]}...")
            error_result = {
                'selected_tables': [],
                'selected_columns': {},
                'reasoning': f"JSON parsing error: {str(json_error)}. Raw response: {response[:200]}...",
                'confidence': 0,
                'success': False,
                'error': f"JSON decode error: {str(json_error)}"
            }
            logger.debug(f"Returning error result: {error_result}")
            return error_result
            
        except Exception as error:
            logger.error(f"General error in table selection: {str(error)}")
            logger.exception("Full exception details:")
            error_result = {
                'selected_tables': [],
                'selected_columns': {},
                'reasoning': f"Error selecting tables and columns: {str(error)}",
                'confidence': 0,
                'success': False,
                'error': str(error)
            }
            logger.debug(f"Returning error result: {error_result}")
            return error_result