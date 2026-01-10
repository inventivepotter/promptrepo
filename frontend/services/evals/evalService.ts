import EvalApi from './api';
import { errorNotification } from '@/lib/notifications';
import { isStandardResponse, isErrorResponse } from '@/types/OpenApiResponse';
import type {
  EvalData,
  EvalMeta,
  EvalSummary,
  EvalExecutionResult,
  TestExecutionResult
} from '@/types/eval';

/**
 * Eval service for DeepEval evaluation management
 * Handles API calls with proper error handling and notifications
 */
export class EvalService {
  /**
   * List all evals in a repository
   * @param repoName - Repository name
   * @returns List of eval summaries
   */
  static async listEvals(repoName: string): Promise<EvalSummary[]> {
    try {
      const result = await EvalApi.listEvals(repoName);

      if (isErrorResponse(result)) {
        errorNotification(
          result.title || 'Failed to Load Evals',
          result.detail || 'Unable to load evals from server.'
        );
        throw new Error(result.detail || 'Failed to load evals');
      }

      if (!isStandardResponse(result) || !result.data) {
        errorNotification(
          'Unexpected Response',
          'Received an unexpected response from the server.'
        );
        throw new Error('Unexpected response format');
      }

      return result.data;
    } catch (error: unknown) {
      // Only show connection error if we haven't already shown an API error
      if (error instanceof Error && !error.message.includes('Failed to load')) {
        errorNotification(
          'Connection Error',
          'Unable to connect to eval service.'
        );
      }
      throw error;
    }
  }

  /**
   * Get specific eval definition
   * @param repoName - Repository name
   * @param filePath - Eval file path
   * @returns Eval metadata with full context
   */
  static async getEval(repoName: string, filePath: string): Promise<EvalData> {
    try {
      const result = await EvalApi.getEval(repoName, filePath);

      if (isErrorResponse(result)) {
        errorNotification(
          result.title || 'Failed to Load Eval',
          result.detail || `Unable to load eval from "${filePath}".`
        );
        throw new Error(result.detail || 'Failed to load eval');
      }

      if (!isStandardResponse(result) || !result.data) {
        errorNotification(
          'Unexpected Response',
          'Received an unexpected response from the server.'
        );
        throw new Error('Unexpected response format');
      }

      // Return just the EvalData portion for backward compatibility
      return { eval: result.data.eval };
    } catch (error: unknown) {
      errorNotification(
        'Connection Error',
        'Unable to connect to eval service.'
      );
      throw error;
    }
  }

  /**
   * Create or update eval
   * @param repoName - Repository name
   * @param evalData - Eval data to save
   * @param filePath - Optional file path for updates (defaults to 'new' for creation)
   * @returns Saved eval metadata with file path
   */
  static async saveEval(repoName: string, evalData: EvalData, filePath?: string): Promise<EvalMeta> {
    try {
      // Use provided filePath or default to 'new' for creation
      const pathToUse = filePath || 'new';
      const result = await EvalApi.saveEval(repoName, pathToUse, evalData);

      if (isErrorResponse(result)) {
        errorNotification(
          result.title || 'Failed to Save Eval',
          result.detail || 'Unable to save eval. Changes may not be saved.'
        );
        throw new Error(result.detail || 'Failed to save eval');
      }

      if (!isStandardResponse(result) || !result.data) {
        errorNotification(
          'Unexpected Response',
          'Received an unexpected response from the server.'
        );
        throw new Error('Unexpected response format');
      }

      // Return the full EvalMeta which includes file_path
      return result.data;
    } catch (error: unknown) {
      errorNotification(
        'Connection Error',
        'Unable to connect to eval service. Changes may not be saved.'
      );
      throw error;
    }
  }

  /**
   * Delete eval
   * @param repoName - Repository name
   * @param evalName - Eval name
   * @returns Success status
   */
  static async deleteEval(repoName: string, evalName: string): Promise<boolean> {
    try {
      const result = await EvalApi.deleteEval(repoName, evalName);

      if (isErrorResponse(result)) {
        errorNotification(
          result.title || 'Failed to Delete Eval',
          result.detail || `Unable to delete eval "${evalName}".`
        );
        throw new Error(result.detail || 'Failed to delete eval');
      }

      if (!isStandardResponse(result) || !result.data) {
        errorNotification(
          'Unexpected Response',
          'Received an unexpected response from the server.'
        );
        throw new Error('Unexpected response format');
      }

      return result.data.deleted;
    } catch (error: unknown) {
      errorNotification(
        'Connection Error',
        'Unable to connect to eval service.'
      );
      throw error;
    }
  }

  /**
   * Execute eval or specific tests
   * @param repoName - Repository name
   * @param filePath - Eval file path
   * @param testNames - Optional array of specific test names to execute
   * @returns Eval execution results
   */
  static async executeEval(
    repoName: string,
    filePath: string,
    testNames?: string[]
  ): Promise<EvalExecutionResult> {
    try {
      const result = await EvalApi.executeEval(repoName, filePath, testNames);

      if (isErrorResponse(result)) {
        errorNotification(
          result.title || 'Eval Execution Failed',
          result.detail || `Unable to execute eval.`
        );
        throw new Error(result.detail || 'Eval execution failed');
      }

      if (!isStandardResponse(result) || !result.data) {
        errorNotification(
          'Unexpected Response',
          'Received an unexpected response from the server.'
        );
        throw new Error('Unexpected response format');
      }

      return result.data;
    } catch (error: unknown) {
      errorNotification(
        'Connection Error',
        'Unable to connect to eval execution service.'
      );
      throw error;
    }
  }

  /**
   * Execute single test
   * @param repoName - Repository name
   * @param filePath - Eval file path
   * @param testName - Test name
   * @returns Test execution result
   */
  static async executeSingleTest(
    repoName: string,
    filePath: string,
    testName: string
  ): Promise<TestExecutionResult> {
    try {
      const result = await EvalApi.executeSingleTest(repoName, filePath, testName);

      if (isErrorResponse(result)) {
        errorNotification(
          result.title || 'Test Execution Failed',
          result.detail || `Unable to execute test "${testName}".`
        );
        throw new Error(result.detail || 'Test execution failed');
      }

      if (!isStandardResponse(result) || !result.data) {
        errorNotification(
          'Unexpected Response',
          'Received an unexpected response from the server.'
        );
        throw new Error('Unexpected response format');
      }

      return result.data;
    } catch (error: unknown) {
      errorNotification(
        'Connection Error',
        'Unable to connect to eval execution service.'
      );
      throw error;
    }
  }

  /**
   * Get execution history for eval
   * @param repoName - Repository name
   * @param filePath - Eval file path
   * @param limit - Maximum number of executions to return
   * @returns List of execution results
   */
  static async getExecutionHistory(
    repoName: string,
    filePath: string,
    limit: number = 10
  ): Promise<EvalExecutionResult[]> {
    try {
      const result = await EvalApi.getExecutionHistory(repoName, filePath, limit);

      if (isErrorResponse(result)) {
        errorNotification(
          result.title || 'Failed to Load Execution History',
          result.detail || `Unable to load execution history.`
        );
        throw new Error(result.detail || 'Failed to load execution history');
      }

      if (!isStandardResponse(result) || !result.data) {
        errorNotification(
          'Unexpected Response',
          'Received an unexpected response from the server.'
        );
        throw new Error('Unexpected response format');
      }

      return result.data;
    } catch (error: unknown) {
      errorNotification(
        'Connection Error',
        'Unable to connect to eval service.'
      );
      throw error;
    }
  }

  /**
   * Get latest execution for eval
   * @param repoName - Repository name
   * @param filePath - Eval file path
   * @returns Latest execution result or null
   */
  static async getLatestExecution(
    repoName: string,
    filePath: string
  ): Promise<EvalExecutionResult | null> {
    try {
      const result = await EvalApi.getLatestExecution(repoName, filePath);

      if (isErrorResponse(result)) {
        errorNotification(
          result.title || 'Failed to Load Latest Execution',
          result.detail || `Unable to load latest execution.`
        );
        throw new Error(result.detail || 'Failed to load latest execution');
      }

      if (!isStandardResponse(result)) {
        errorNotification(
          'Unexpected Response',
          'Received an unexpected response from the server.'
        );
        throw new Error('Unexpected response format');
      }

      return result.data ?? null;
    } catch (error: unknown) {
      errorNotification(
        'Connection Error',
        'Unable to connect to eval service.'
      );
      throw error;
    }
  }
}