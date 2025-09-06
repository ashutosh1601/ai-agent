import time
from typing import Dict, Any, List, Optional
from .components.input_refinement import InputRefinement
from .components.query_selector import QuerySelector
from .components.table_selector import TableSelector
from .components.query_generator import QueryGenerator


class AIAgent:
    """Main AI agent for SQL query generation."""
    
    def __init__(self, config: Dict[str, Any] = None):
        config = config or {}
        
        self.input_refinement = InputRefinement()
        self.query_selector = QuerySelector(config.get('example_queries', []))
        self.table_selector = TableSelector(config.get('table_metadata', {}))
        self.query_generator = QueryGenerator()
        self.config = config
    
    def add_example_query(self, query: str, description: str) -> None:
        """Add an example query to the query selector."""
        self.query_selector.add_example_query(query, description)
    
    def add_table_metadata(self, table_name: str, metadata: Dict[str, Any]) -> None:
        """Add table metadata to the table selector."""
        self.table_selector.add_table_metadata(table_name, metadata)
    
    async def process_query(self, user_input: str) -> Dict[str, Any]:
        """Process a user query through the complete AI agent pipeline."""
        start_time = time.time()
        result = {
            'user_input': user_input,
            'steps': {},
            'final_query': None,
            'success': False,
            'processing_time': 0
        }
        
        try:
            print('🤖 Starting AI Agent processing...')
            
            print('📝 Step 1: Refining user input...')
            result['steps']['refinement'] = await self.input_refinement.refine_user_input(user_input)
            
            if not result['steps']['refinement']['success']:
                raise Exception(f"Input refinement failed: {result['steps']['refinement']['error']}")
            
            print('🔍 Step 2: Selecting appropriate query pattern...')
            result['steps']['query_selection'] = await self.query_selector.select_best_query(
                result['steps']['refinement']['refined']
            )
            
            print('🗂️ Step 3: Selecting tables and columns...')
            result['steps']['table_selection'] = await self.table_selector.select_tables_and_columns(
                result['steps']['refinement']['refined']
            )
            
            if not result['steps']['table_selection']['success']:
                raise Exception(f"Table selection failed: {result['steps']['table_selection']['error']}")
            
            print('⚡ Step 4: Generating final Redshift query...')
            result['steps']['query_generation'] = await self.query_generator.generate_redshift_query(
                result['steps']['refinement']['refined'],
                result['steps']['query_selection']['selected_query'],
                result['steps']['table_selection']['selected_tables'],
                result['steps']['table_selection']['selected_columns']
            )
            
            if not result['steps']['query_generation']['success']:
                raise Exception(f"Query generation failed: {result['steps']['query_generation']['error']}")
            
            print('✅ Step 5: Validating generated query...')
            result['steps']['validation'] = self.query_generator.validate_query(
                result['steps']['query_generation']['query']
            )
            
            result['final_query'] = result['steps']['query_generation']['query']
            result['success'] = True
            result['processing_time'] = int((time.time() - start_time) * 1000)
            
            print(f'🎉 Processing completed successfully in {result["processing_time"]}ms')
            
            return result
            
        except Exception as error:
            result['success'] = False
            result['error'] = str(error)
            result['processing_time'] = int((time.time() - start_time) * 1000)
            
            print(f'❌ Processing failed: {str(error)}')
            
            return result
    
    def get_processing_summary(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Get a summary of the processing steps."""
        summary = {
            'success': result['success'],
            'processing_time': result['processing_time'],
            'steps': {}
        }
        
        if 'refinement' in result['steps']:
            summary['steps']['refinement'] = {
                'original': result['steps']['refinement']['original'],
                'refined': result['steps']['refinement']['refined']
            }
        
        if 'query_selection' in result['steps']:
            summary['steps']['query_selection'] = {
                'confidence': result['steps']['query_selection']['confidence'],
                'reasoning': result['steps']['query_selection']['reasoning']
            }
        
        if 'table_selection' in result['steps']:
            summary['steps']['table_selection'] = {
                'selected_tables': result['steps']['table_selection']['selected_tables'],
                'confidence': result['steps']['table_selection']['confidence']
            }
        
        if 'validation' in result['steps']:
            summary['steps']['validation'] = {
                'is_valid': result['steps']['validation']['is_valid'],
                'suggestions': result['steps']['validation']['suggestions']
            }
        
        return summary