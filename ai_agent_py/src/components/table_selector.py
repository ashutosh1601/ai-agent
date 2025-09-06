import json
from typing import Dict, Any, List
from ..utils.ollama_client import call_ollama


class TableSelector:
    """Component for selecting relevant tables and columns."""
    
    def __init__(self, table_metadata: Dict[str, Any] = None):
        self.table_metadata = table_metadata or {}
    
    def add_table_metadata(self, table_name: str, metadata: Dict[str, Any]) -> None:
        """Add metadata for a table."""
        self.table_metadata[table_name] = metadata
    
    async def select_tables_and_columns(self, user_prompt: str) -> Dict[str, Any]:
        """Select relevant tables and columns for the user prompt."""
        if not self.table_metadata:
            return {
                'selected_tables': [],
                'selected_columns': {},
                'reasoning': "No table metadata available"
            }
        
        metadata_text = '\n'.join([
            f"""
Table: {table_name}
Description: {metadata.get('description', 'No description available')}
Columns:
{chr(10).join([f"  - {col['name']} ({col['type']}): {col.get('description', 'No description')}" for col in metadata['columns']])}
"""
            for table_name, metadata in self.table_metadata.items()
        ])
        
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
        
        try:
            response = await call_ollama(prompt)
            result = json.loads(response)
            
            return {
                'selected_tables': result['selectedTables'],
                'selected_columns': result['selectedColumns'],
                'reasoning': result['reasoning'],
                'confidence': result['confidence'],
                'success': True
            }
        except Exception as error:
            return {
                'selected_tables': [],
                'selected_columns': {},
                'reasoning': f"Error selecting tables and columns: {str(error)}",
                'confidence': 0,
                'success': False,
                'error': str(error)
            }