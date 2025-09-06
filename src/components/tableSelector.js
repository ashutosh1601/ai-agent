import { callOllama } from '../utils/ollama.js';

export class TableSelector {
  constructor(tableMetadata = {}) {
    this.tableMetadata = tableMetadata;
  }

  addTableMetadata(tableName, metadata) {
    this.tableMetadata[tableName] = metadata;
  }

  async selectTablesAndColumns(userPrompt) {
    if (Object.keys(this.tableMetadata).length === 0) {
      return {
        selectedTables: [],
        selectedColumns: {},
        reasoning: "No table metadata available"
      };
    }

    const metadataText = Object.entries(this.tableMetadata)
      .map(([tableName, metadata]) => `
Table: ${tableName}
Description: ${metadata.description || 'No description available'}
Columns:
${metadata.columns.map(col => `  - ${col.name} (${col.type}): ${col.description || 'No description'}`).join('\n')}
`)
      .join('\n');

    const prompt = `
You are a database expert. Given a user's request and database table metadata, identify the most relevant tables and columns needed to fulfill the request.

User Request: "${userPrompt}"

Available Tables and Columns:
${metadataText}

Please analyze the user request and:
1. Identify which tables are needed
2. Identify which specific columns from each table are required
3. Explain your reasoning

Respond in JSON format:
{
  "selectedTables": ["table1", "table2"],
  "selectedColumns": {
    "table1": ["column1", "column2"],
    "table2": ["column3", "column4"]
  },
  "reasoning": "<explanation_of_selections>",
  "confidence": <confidence_score_0_to_100>
}
`;

    try {
      const response = await callOllama(prompt);
      const result = JSON.parse(response);
      
      return {
        selectedTables: result.selectedTables,
        selectedColumns: result.selectedColumns,
        reasoning: result.reasoning,
        confidence: result.confidence,
        success: true
      };
    } catch (error) {
      return {
        selectedTables: [],
        selectedColumns: {},
        reasoning: `Error selecting tables and columns: ${error.message}`,
        confidence: 0,
        success: false,
        error: error.message
      };
    }
  }
}