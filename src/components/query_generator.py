import re
import logging
from typing import Dict, Any, List, Optional
from ..utils.ollama_client import call_ollama

# Set up logger
logger = logging.getLogger(__name__)


class QueryGenerator:
    """Component for generating and validating SQL queries."""
    
    async def generate_redshift_query(
        self, 
        user_prompt: str, 
        selected_query: Optional[str], 
        selected_tables: List[str], 
        selected_columns: Dict[str, List[str]]
    ) -> Dict[str, Any]:
        """Generate a Redshift SQL query based on the provided information."""
        logger.info(f"Starting SQL query generation for prompt: '{user_prompt}'")
        logger.info(f"Selected tables: {selected_tables}")
        logger.info(f"Selected columns: {selected_columns}")
        logger.debug(f"Reference query: {selected_query}")
        
        tables_info = '\n\n'.join([
            f"Table: {table}\nColumns: {', '.join(selected_columns.get(table, []))}"
            for table in selected_tables
        ])
        
        logger.debug(f"Generated tables info: {tables_info}")
        
        prompt = f"""
You are an expert Redshift SQL developer. Generate a complete, optimized Redshift SQL query based on the provided information.

User Request: "{user_prompt}"

Reference Query Pattern: {selected_query or 'No reference query provided'}

Available Tables and Columns:
{tables_info}

Requirements:
1. Generate a complete, syntactically correct Redshift SQL query
2. Use appropriate Redshift-specific functions and optimizations where applicable
3. Include proper JOINs if multiple tables are needed
4. Add appropriate WHERE clauses based on the user request
5. Use proper column aliases for readability
6. Ensure the query follows Redshift best practices

Respond with ONLY the SQL query, no additional text or formatting.
"""
        
        logger.info("Sending prompt to Ollama API for SQL generation")
        logger.debug(f"Full prompt (length: {len(prompt)} chars): {prompt[:300]}...")
        
        try:
            response = await call_ollama(prompt)
            logger.info(f"Received SQL query response from Ollama (length: {len(response)} chars)")
            
            generated_query = response.strip()
            logger.info("SQL query generation completed successfully")
            logger.debug(f"Generated query: {generated_query}")
            
            result = {
                'query': generated_query,
                'success': True,
                'metadata': {
                    'user_prompt': user_prompt,
                    'selected_query': selected_query,
                    'selected_tables': selected_tables,
                    'selected_columns': selected_columns
                }
            }
            
            logger.debug(f"Full generation result: {result}")
            return result
            
        except Exception as error:
            logger.error(f"SQL query generation failed: {str(error)}")
            logger.exception("Full exception details:")
            
            error_result = {
                'query': None,
                'success': False,
                'error': str(error),
                'metadata': {
                    'user_prompt': user_prompt,
                    'selected_query': selected_query,
                    'selected_tables': selected_tables,
                    'selected_columns': selected_columns
                }
            }
            
            logger.debug(f"Returning error result: {error_result}")
            return error_result
    
    def validate_query(self, query: str) -> Dict[str, Any]:
        """Validate the generated SQL query."""
        logger.info(f"Starting query validation for query (length: {len(query)} chars)")
        logger.debug(f"Query to validate: {query}")
        
        basic_checks = {
            'has_select': bool(re.search(r'SELECT', query, re.IGNORECASE)),
            'has_from': bool(re.search(r'FROM', query, re.IGNORECASE)),
            'proper_syntax': query.strip().endswith(';') or ';' not in query,
            'not_empty': len(query.strip()) > 0
        }
        
        logger.debug(f"Validation checks: {basic_checks}")
        
        is_valid = all(basic_checks.values())
        
        result = {
            'is_valid': is_valid,
            'checks': basic_checks,
            'suggestions': self._generate_suggestions(basic_checks)
        }
        
        logger.info(f"Query validation completed. Valid: {is_valid}")
        if not is_valid:
            logger.warning(f"Query validation failed. Failed checks: {[k for k, v in basic_checks.items() if not v]}")
            logger.info(f"Suggestions: {result['suggestions']}")
        
        logger.debug(f"Full validation result: {result}")
        return result
    
    def _generate_suggestions(self, checks: Dict[str, bool]) -> List[str]:
        """Generate suggestions based on validation checks."""
        logger.debug("Generating validation suggestions")
        suggestions = []
        
        if not checks['has_select']:
            suggestions.append("Query should include a SELECT statement")
        if not checks['has_from']:
            suggestions.append("Query should include a FROM clause")
        if not checks['not_empty']:
            suggestions.append("Query cannot be empty")
        
        logger.debug(f"Generated suggestions: {suggestions}")
        return suggestions