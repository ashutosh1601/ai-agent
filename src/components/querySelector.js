import { callOllama } from '../utils/ollama.js';

export class QuerySelector {
  constructor(exampleQueries = []) {
    this.exampleQueries = exampleQueries;
  }

  addExampleQuery(query, description) {
    this.exampleQueries.push({ query, description });
  }

  async selectBestQuery(userPrompt) {
    if (this.exampleQueries.length === 0) {
      return {
        selectedQuery: null,
        confidence: 0,
        reasoning: "No example queries available"
      };
    }

    const exampleQueriesText = this.exampleQueries
      .map((example, index) => `
Example ${index + 1}:
Description: ${example.description}
SQL Query: ${example.query}
`)
      .join('\n');

    const prompt = `
You are an expert SQL analyst. Given a user's request and a set of example SQL queries, select the most appropriate example query that best matches the user's intent.

User Request: "${userPrompt}"

Available Example Queries:
${exampleQueriesText}

Please analyze the user request and:
1. Select the example query that best matches the user's intent
2. Provide a confidence score (0-100)
3. Explain your reasoning

Respond in JSON format:
{
  "selectedQueryIndex": <index_of_selected_query>,
  "selectedQuery": "<the_selected_sql_query>",
  "confidence": <confidence_score>,
  "reasoning": "<explanation_of_why_this_query_was_selected>"
}
`;

    try {
      const response = await callOllama(prompt);
      const result = JSON.parse(response);
      
      return {
        selectedQuery: result.selectedQuery,
        selectedQueryIndex: result.selectedQueryIndex,
        confidence: result.confidence,
        reasoning: result.reasoning,
        success: true
      };
    } catch (error) {
      return {
        selectedQuery: null,
        confidence: 0,
        reasoning: `Error selecting query: ${error.message}`,
        success: false,
        error: error.message
      };
    }
  }
}