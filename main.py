import asyncio
import sys
import logging
from src.ai_agent import AIAgent
from src.utils.ollama_client import check_ollama_connection, list_ollama_models

# Set up main logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


EXAMPLE_QUERIES = [
    {
        'query': "SELECT customer_id, SUM(order_amount) as total_spent FROM orders WHERE order_date >= '2023-01-01' GROUP BY customer_id ORDER BY total_spent DESC;",
        'description': "Get total spending by customer for orders after a specific date"
    },
    {
        'query': "SELECT p.product_name, COUNT(oi.order_id) as order_count FROM products p JOIN order_items oi ON p.product_id = oi.product_id GROUP BY p.product_name ORDER BY order_count DESC LIMIT 10;",
        'description': "Get top 10 most ordered products"
    },
    {
        'query': "SELECT DATE_TRUNC('month', order_date) as month, SUM(order_amount) as monthly_revenue FROM orders GROUP BY month ORDER BY month;",
        'description': "Get monthly revenue totals"
    }
]

TABLE_METADATA = {
    'customers': {
        'description': "Customer information table",
        'columns': [
            {'name': "customer_id", 'type': "INTEGER", 'description': "Unique customer identifier"},
            {'name': "customer_name", 'type': "VARCHAR(100)", 'description': "Customer full name"},
            {'name': "email", 'type': "VARCHAR(255)", 'description': "Customer email address"},
            {'name': "registration_date", 'type': "DATE", 'description': "Date customer registered"},
            {'name': "country", 'type': "VARCHAR(50)", 'description': "Customer's country"}
        ]
    },
    'orders': {
        'description': "Order transactions table",
        'columns': [
            {'name': "order_id", 'type': "INTEGER", 'description': "Unique order identifier"},
            {'name': "customer_id", 'type': "INTEGER", 'description': "Customer who placed the order"},
            {'name': "order_date", 'type': "DATE", 'description': "Date the order was placed"},
            {'name': "order_amount", 'type': "DECIMAL(10,2)", 'description': "Total order amount"},
            {'name': "order_status", 'type': "VARCHAR(20)", 'description': "Current order status"}
        ]
    },
    'products': {
        'description': "Product catalog table",
        'columns': [
            {'name': "product_id", 'type': "INTEGER", 'description': "Unique product identifier"},
            {'name': "product_name", 'type': "VARCHAR(200)", 'description': "Product name"},
            {'name': "category", 'type': "VARCHAR(50)", 'description': "Product category"},
            {'name': "price", 'type': "DECIMAL(8,2)", 'description': "Product price"},
            {'name': "stock_quantity", 'type': "INTEGER", 'description': "Available stock"}
        ]
    },
    'order_items': {
        'description': "Individual items within orders",
        'columns': [
            {'name': "order_item_id", 'type': "INTEGER", 'description': "Unique order item identifier"},
            {'name': "order_id", 'type': "INTEGER", 'description': "Associated order"},
            {'name': "product_id", 'type': "INTEGER", 'description': "Product being ordered"},
            {'name': "quantity", 'type': "INTEGER", 'description': "Quantity ordered"},
            {'name': "unit_price", 'type': "DECIMAL(8,2)", 'description': "Price per unit"}
        ]
    }
}


async def main():
    """Main entry point for the AI SQL Agent."""
    logger.info("Starting AI SQL Agent Demo")
    print('🚀 AI SQL Agent Demo (Python)\n')
    
    logger.info("Checking Ollama connection")
    print('🔌 Checking Ollama connection...')
    is_connected = await check_ollama_connection()
    
    if not is_connected:
        logger.error("Failed to connect to Ollama")
        print('❌ Cannot connect to Ollama. Please ensure Ollama is running on http://localhost:11434')
        print('💡 Install Ollama from: https://ollama.ai')
        print('💡 Start Ollama with: ollama serve')
        print('💡 Pull a model with: ollama pull llama3.1')
        return
    
    logger.info("Ollama connection successful")
    print('✅ Ollama connection successful')
    
    try:
        logger.info("Listing available Ollama models")
        models = await list_ollama_models()
        logger.info(f"Found {len(models)} available models: {models}")
        print(f'📋 Available models: {", ".join(models)}')
    except Exception as e:
        logger.warning(f"Could not list available models: {str(e)}")
        print('⚠️  Could not list available models')
    
    logger.info(f"Initializing AI Agent with {len(EXAMPLE_QUERIES)} example queries and {len(TABLE_METADATA)} tables")
    agent = AIAgent({
        'example_queries': EXAMPLE_QUERIES,
        'table_metadata': TABLE_METADATA
    })
    
    test_queries = [
        "Show me the top 5 customers by total spending this year",
        "What are the best selling products in electronics category?",
        "Get monthly sales trends for the last 6 months"
    ]
    
    logger.info(f"Starting processing of {len(test_queries)} test queries")
    
    for i, query in enumerate(test_queries, 1):
        logger.info(f"Processing query {i}/{len(test_queries)}: '{query}'")
        print(f'\n{"=" * 60}')
        print(f'Query: {query}')
        print(f'{"=" * 60}')
        
        result = await agent.process_query(query)
        
        if result['success']:
            logger.info(f"Query {i} processed successfully in {result['processing_time']}ms")
            print('\n📊 Generated SQL Query:')
            print('```sql')
            print(result['final_query'])
            print('```\n')
            
            summary = agent.get_processing_summary(result)
            logger.debug(f"Query {i} summary: {summary}")
            print('📋 Processing Summary:')
            print(f'- Refined Input: "{summary["steps"].get("refinement", {}).get("refined", "N/A")}"')
            print(f'- Selected Tables: {", ".join(summary["steps"].get("table_selection", {}).get("selected_tables", [])) or "N/A"}')
            print(f'- Query Confidence: {summary["steps"].get("query_selection", {}).get("confidence", "N/A")}%')
            print(f'- Processing Time: {summary["processing_time"]}ms')
            print(f'- Query Valid: {"✅" if summary["steps"].get("validation", {}).get("is_valid") else "❌"}')
        else:
            logger.error(f"Query {i} failed: {result['error']}")
            print(f'\n❌ Error: {result["error"]}')

    logger.info("AI SQL Agent Demo completed")


if __name__ == "__main__":
    logger.info("Starting main execution")
    asyncio.run(main())