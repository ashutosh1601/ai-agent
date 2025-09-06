import { Ollama } from 'ollama';
import dotenv from 'dotenv';

dotenv.config();

const ollama = new Ollama({
  host: process.env.OLLAMA_HOST || 'http://localhost:11434'
});

export async function callOllama(prompt, model = null) {
  try {
    const response = await ollama.chat({
      model: model || process.env.OLLAMA_MODEL || 'llama3.1',
      messages: [
        {
          role: 'user',
          content: prompt
        }
      ],
      options: {
        temperature: 0.1,
        num_predict: 2000
      }
    });

    return response.message.content;
  } catch (error) {
    console.error('Ollama API Error:', error);
    throw new Error(`Ollama API call failed: ${error.message}`);
  }
}

export async function listOllamaModels() {
  try {
    const models = await ollama.list();
    return models.models.map(model => model.name);
  } catch (error) {
    console.error('Error listing Ollama models:', error);
    throw new Error(`Failed to list Ollama models: ${error.message}`);
  }
}

export async function checkOllamaConnection() {
  try {
    await ollama.list();
    return true;
  } catch (error) {
    return false;
  }
}