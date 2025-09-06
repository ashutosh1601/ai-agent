import re
from typing import Dict, Any, List, Optional
from ..utils.ollama_client import call_ollama


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
        
        tables_info = '\n\n'.join([
            f"Table: {table}\nColumns: {', '.join(selected_columns.get(table, []))}"
            for table in selected_tables
        ])
        
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
        
        try:
            response = await call_ollama(prompt)
            
            return {
                'query': response.strip(),
                'success': True,
                'metadata': {
                    'user_prompt': user_prompt,
                    'selected_query': selected_query,
                    'selected_tables': selected_tables,
                    'selected_columns': selected_columns
                }
            }
        except Exception as error:
            return {
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
    
    def validate_query(self, query: str) -> Dict[str, Any]:
        """Validate the generated SQL query."""
        basic_checks = {
            'has_select': bool(re.search(r'SELECT', query, re.IGNORECASE)),
            'has_from': bool(re.search(r'FROM', query, re.IGNORECASE)),
            'proper_syntax': query.strip().endswith(';') or ';' not in query,
            'not_empty': len(query.strip()) > 0
        }
        
        is_valid = all(basic_checks.values())
        
        return {
            'is_valid': is_valid,
            'checks': basic_checks,
            'suggestions': self._generate_suggestions(basic_checks)
        }
    
    def _generate_suggestions(self, checks: Dict[str, bool]) -> List[str]:
        """Generate suggestions based on validation checks."""
        suggestions = []
        
        if not checks['has_select']:
            suggestions.append("Query should include a SELECT statement")
        if not checks['has_from']:
            suggestions.append("Query should include a FROM clause")
        if not checks['not_empty']:
            suggestions.append("Query cannot be empty")
        
        return suggestions