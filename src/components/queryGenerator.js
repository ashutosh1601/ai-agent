import { callOllama } from '../utils/ollama.js';

export class QueryGenerator {
  async generateRedshiftQuery(userPrompt, selectedQuery, selectedTables, selectedColumns) {
    const tablesInfo = selectedTables.map(table => {
      const columns = selectedColumns[table] || [];
      return `Table: ${table}\nColumns: ${columns.join(', ')}`;
    }).join('\n\n');

    const prompt = `
You are an expert Redshift SQL developer. Generate a complete, optimized Redshift SQL query based on the provided information.

User Request: "${userPrompt}"

Reference Query Pattern: ${selectedQuery || 'No reference query provided'}

Available Tables and Columns:
${tablesInfo}

Requirements:
1. Generate a complete, syntactically correct Redshift SQL query
2. Use appropriate Redshift-specific functions and optimizations where applicable
3. Include proper JOINs if multiple tables are needed
4. Add appropriate WHERE clauses based on the user request
5. Use proper column aliases for readability
6. Ensure the query follows Redshift best practices

Respond with ONLY the SQL query, no additional text or formatting.
`;

    try {
      const response = await callOllama(prompt);
      
      return {
        query: response.trim(),
        success: true,
        metadata: {
          userPrompt,
          selectedQuery,
          selectedTables,
          selectedColumns
        }
      };
    } catch (error) {
      return {
        query: null,
        success: false,
        error: error.message,
        metadata: {
          userPrompt,
          selectedQuery,
          selectedTables,
          selectedColumns
        }
      };
    }
  }

  validateQuery(query) {
    const basicChecks = {
      hasSelect: /SELECT/i.test(query),
      hasFrom: /FROM/i.test(query),
      properSyntax: query.trim().endsWith(';') || !query.includes(';'),
      notEmpty: query.trim().length > 0
    };

    const isValid = Object.values(basicChecks).every(check => check);
    
    return {
      isValid,
      checks: basicChecks,
      suggestions: this.generateSuggestions(basicChecks)
    };
  }

  generateSuggestions(checks) {
    const suggestions = [];
    
    if (!checks.hasSelect) suggestions.push("Query should include a SELECT statement");
    if (!checks.hasFrom) suggestions.push("Query should include a FROM clause");
    if (!checks.notEmpty) suggestions.push("Query cannot be empty");
    
    return suggestions;
  }
}