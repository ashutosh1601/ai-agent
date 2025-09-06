import { callOllama } from '../utils/ollama.js';

export class InputRefinement {
  async refineUserInput(userInput) {
    const prompt = `
You are an AI assistant that refines user queries for SQL generation. 
Your task is to take a user's natural language query and refine it to be more specific, clear, and suitable for SQL query generation.

User Input: "${userInput}"

Please refine this input by:
1. Clarifying any ambiguous terms
2. Adding specific details that would be helpful for SQL generation
3. Identifying the main intent (SELECT, UPDATE, DELETE, etc.)
4. Suggesting specific data types or ranges where appropriate

Return only the refined query in a clear, concise format.
`;

    try {
      const response = await callOllama(prompt);
      return {
        original: userInput,
        refined: response,
        success: true
      };
    } catch (error) {
      return {
        original: userInput,
        refined: userInput,
        success: false,
        error: error.message
      };
    }
  }
}