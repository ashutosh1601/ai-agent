# AI SQL Agent

An intelligent AI agent that generates Redshift SQL queries from natural language input through a multi-step process.

## Features

1. **Input Refinement**: Takes user input and refines it for better SQL generation
2. **Query Pattern Selection**: Matches user intent with example SQL query patterns
3. **Table & Column Selection**: Analyzes table metadata to select appropriate tables and columns
4. **Redshift Query Generation**: Generates optimized Redshift SQL queries

## Setup

1. Install dependencies:
```bash
npm install
```

2. Install and start Ollama:
```bash
# Install Ollama from https://ollama.ai
# Then start the service
ollama serve

# Pull a model (in another terminal)
ollama pull llama3.1
```

3. (Optional) Create a `.env` file to customize settings:
```bash
cp .env.example .env
```

Edit `.env` to customize:
```
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.1
```

## Usage

### Run the demo:
```bash
npm start
```

### Use programmatically:
```javascript
import { AIAgent } from './src/aiAgent.js';

const agent = new AIAgent({
  exampleQueries: [
    {
      query: "SELECT * FROM customers WHERE country = 'US'",
      description: "Get all US customers"
    }
  ],
  tableMetadata: {
    customers: {
      description: "Customer information",
      columns: [
        { name: "id", type: "INTEGER", description: "Customer ID" },
        { name: "name", type: "VARCHAR", description: "Customer name" }
      ]
    }
  }
});

const result = await agent.processQuery("Show me all customers from the United States");
console.log(result.finalQuery);
```

## Architecture

- `src/components/inputRefinement.js` - Refines user input
- `src/components/querySelector.js` - Selects best matching query pattern
- `src/components/tableSelector.js` - Selects relevant tables and columns
- `src/components/queryGenerator.js` - Generates final Redshift query
- `src/aiAgent.js` - Main orchestrator class
- `src/utils/ollama.js` - Ollama API utility

## Configuration

The agent can be configured with:
- Example SQL queries for pattern matching
- Table metadata for schema understanding
- Custom Ollama host and model settings