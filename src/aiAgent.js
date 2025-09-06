import { InputRefinement } from './components/inputRefinement.js';
import { QuerySelector } from './components/querySelector.js';
import { TableSelector } from './components/tableSelector.js';
import { QueryGenerator } from './components/queryGenerator.js';

export class AIAgent {
  constructor(config = {}) {
    this.inputRefinement = new InputRefinement();
    this.querySelector = new QuerySelector(config.exampleQueries || []);
    this.tableSelector = new TableSelector(config.tableMetadata || {});
    this.queryGenerator = new QueryGenerator();
    this.config = config;
  }

  addExampleQuery(query, description) {
    this.querySelector.addExampleQuery(query, description);
  }

  addTableMetadata(tableName, metadata) {
    this.tableSelector.addTableMetadata(tableName, metadata);
  }

  async processQuery(userInput) {
    const startTime = Date.now();
    const result = {
      userInput,
      steps: {},
      finalQuery: null,
      success: false,
      processingTime: 0
    };

    try {
      console.log('🤖 Starting AI Agent processing...');
      
      console.log('📝 Step 1: Refining user input...');
      result.steps.refinement = await this.inputRefinement.refineUserInput(userInput);
      
      if (!result.steps.refinement.success) {
        throw new Error(`Input refinement failed: ${result.steps.refinement.error}`);
      }

      console.log('🔍 Step 2: Selecting appropriate query pattern...');
      result.steps.querySelection = await this.querySelector.selectBestQuery(
        result.steps.refinement.refined
      );

      console.log('🗂️ Step 3: Selecting tables and columns...');
      result.steps.tableSelection = await this.tableSelector.selectTablesAndColumns(
        result.steps.refinement.refined
      );

      if (!result.steps.tableSelection.success) {
        throw new Error(`Table selection failed: ${result.steps.tableSelection.error}`);
      }

      console.log('⚡ Step 4: Generating final Redshift query...');
      result.steps.queryGeneration = await this.queryGenerator.generateRedshiftQuery(
        result.steps.refinement.refined,
        result.steps.querySelection.selectedQuery,
        result.steps.tableSelection.selectedTables,
        result.steps.tableSelection.selectedColumns
      );

      if (!result.steps.queryGeneration.success) {
        throw new Error(`Query generation failed: ${result.steps.queryGeneration.error}`);
      }

      console.log('✅ Step 5: Validating generated query...');
      result.steps.validation = this.queryGenerator.validateQuery(
        result.steps.queryGeneration.query
      );

      result.finalQuery = result.steps.queryGeneration.query;
      result.success = true;
      result.processingTime = Date.now() - startTime;

      console.log(`🎉 Processing completed successfully in ${result.processingTime}ms`);
      
      return result;

    } catch (error) {
      result.success = false;
      result.error = error.message;
      result.processingTime = Date.now() - startTime;
      
      console.error(`❌ Processing failed: ${error.message}`);
      
      return result;
    }
  }

  getProcessingSummary(result) {
    const summary = {
      success: result.success,
      processingTime: result.processingTime,
      steps: {}
    };

    if (result.steps.refinement) {
      summary.steps.refinement = {
        original: result.steps.refinement.original,
        refined: result.steps.refinement.refined
      };
    }

    if (result.steps.querySelection) {
      summary.steps.querySelection = {
        confidence: result.steps.querySelection.confidence,
        reasoning: result.steps.querySelection.reasoning
      };
    }

    if (result.steps.tableSelection) {
      summary.steps.tableSelection = {
        selectedTables: result.steps.tableSelection.selectedTables,
        confidence: result.steps.tableSelection.confidence
      };
    }

    if (result.steps.validation) {
      summary.steps.validation = {
        isValid: result.steps.validation.isValid,
        suggestions: result.steps.validation.suggestions
      };
    }

    return summary;
  }
}