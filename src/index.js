import { AIAgent } from './aiAgent.js';
import { checkOllamaConnection, listOllamaModels } from './utils/ollama.js';

const exampleQueries = [
  {
    query: "SELECT customer_id, SUM(order_amount) as total_spent FROM orders WHERE order_date >= '2023-01-01' GROUP BY customer_id ORDER BY total_spent DESC;",
    description: "Get total spending by customer for orders after a specific date"
  },
  {
    query: "SELECT p.product_name, COUNT(oi.order_id) as order_count FROM products p JOIN order_items oi ON p.product_id = oi.product_id GROUP BY p.product_name ORDER BY order_count DESC LIMIT 10;",
    description: "Get top 10 most ordered products"
  },
  {
    query: "SELECT DATE_TRUNC('month', order_date) as month, SUM(order_amount) as monthly_revenue FROM orders GROUP BY month ORDER BY month;",
    description: "Get monthly revenue totals"
  }
];

const tableMetadata = {
  customers: {
    description: "Customer information table",
    columns: [
      { name: "customer_id", type: "INTEGER", description: "Unique customer identifier" },
      { name: "customer_name", type: "VARCHAR(100)", description: "Customer full name" },
      { name: "email", type: "VARCHAR(255)", description: "Customer email address" },
      { name: "registration_date", type: "DATE", description: "Date customer registered" },
      { name: "country", type: "VARCHAR(50)", description: "Customer's country" }
    ]
  },
  orders: {
    description: "Order transactions table",
    columns: [
      { name: "order_id", type: "INTEGER", description: "Unique order identifier" },
      { name: "customer_id", type: "INTEGER", description: "Customer who placed the order" },
      { name: "order_date", type: "DATE", description: "Date the order was placed" },
      { name: "order_amount", type: "DECIMAL(10,2)", description: "Total order amount" },
      { name: "order_status", type: "VARCHAR(20)", description: "Current order status" }
    ]
  },
  products: {
    description: "Product catalog table",
    columns: [
      { name: "product_id", type: "INTEGER", description: "Unique product identifier" },
      { name: "product_name", type: "VARCHAR(200)", description: "Product name" },
      { name: "category", type: "VARCHAR(50)", description: "Product category" },
      { name: "price", type: "DECIMAL(8,2)", description: "Product price" },
      { name: "stock_quantity", type: "INTEGER", description: "Available stock" }
    ]
  },
  order_items: {
    description: "Individual items within orders",
    columns: [
      { name: "order_item_id", type: "INTEGER", description: "Unique order item identifier" },
      { name: "order_id", type: "INTEGER", description: "Associated order" },
      { name: "product_id", type: "INTEGER", description: "Product being ordered" },
      { name: "quantity", type: "INTEGER", description: "Quantity ordered" },
      { name: "unit_price", type: "DECIMAL(8,2)", description: "Price per unit" }
    ]
  }
};

async function main() {
  console.log('🚀 AI SQL Agent Demo\n');
  
  console.log('🔌 Checking Ollama connection...');
  const isConnected = await checkOllamaConnection();
  
  if (!isConnected) {
    console.error('❌ Cannot connect to Ollama. Please ensure Ollama is running on http://localhost:11434');
    console.log('💡 Install Ollama from: https://ollama.ai');
    console.log('💡 Start Ollama with: ollama serve');
    console.log('💡 Pull a model with: ollama pull llama3.1');
    return;
  }
  
  console.log('✅ Ollama connection successful');
  
  try {
    const models = await listOllamaModels();
    console.log(`📋 Available models: ${models.join(', ')}`);
  } catch (error) {
    console.warn('⚠️  Could not list available models');
  }
  
  const agent = new AIAgent({
    exampleQueries,
    tableMetadata
  });

  const testQueries = [
    "Show me the top 5 customers by total spending this year",
    "What are the best selling products in electronics category?",
    "Get monthly sales trends for the last 6 months"
  ];
  
  for (const query of testQueries) {
    console.log(`\n${'='.repeat(60)}`);
    console.log(`Query: ${query}`);
    console.log(`${'='.repeat(60)}`);
    
    const result = await agent.processQuery(query);
    
    if (result.success) {
      console.log('\n📊 Generated SQL Query:');
      console.log('```sql');
      console.log(result.finalQuery);
      console.log('```\n');
      
      const summary = agent.getProcessingSummary(result);
      console.log('📋 Processing Summary:');
      console.log(`- Refined Input: "${summary.steps.refinement?.refined}"`);
      console.log(`- Selected Tables: ${summary.steps.tableSelection?.selectedTables?.join(', ') || 'N/A'}`);
      console.log(`- Query Confidence: ${summary.steps.querySelection?.confidence || 'N/A'}%`);
      console.log(`- Processing Time: ${summary.processingTime}ms`);
      console.log(`- Query Valid: ${summary.steps.validation?.isValid ? '✅' : '❌'}`);
    } else {
      console.log(`\n❌ Error: ${result.error}`);
    }
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(console.error);
}