import EvalApi from './api';
import { errorNotification } from '@/lib/notifications';
import { isStandardResponse, isErrorResponse } from '@/types/OpenApiResponse';
import type {
  EvalSuiteData,
  EvalSuiteSummary,
  EvalSuiteExecutionResult,
  EvalExecutionResult
} from '@/types/eval';

/**
 * Eval service for DeepEval evaluation management
 * Handles API calls with proper error handling and notifications
 */
export class EvalService {
  /**
   * List all eval suites in a repository
   * @param repoName - Repository name
   * @returns List of eval suite summaries
   */
  static async listEvalSuites(repoName: string): Promise<EvalSuiteSummary[]> {
    try {
      const result = await EvalApi.listEvalSuites(repoName);

      if (isErrorResponse(result)) {
        errorNotification(
          result.title || 'Failed to Load Eval Suites',
          result.detail || 'Unable to load eval suites from server.'
        );
        throw new Error(result.detail || 'Failed to load eval suites');
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
   * Get specific eval suite definition
   * @param repoName - Repository name
   * @param suiteName - Eval suite name
   * @returns Eval suite data
   */
  static async getEvalSuite(repoName: string, suiteName: string): Promise<EvalSuiteData> {
    try {
      const result = await EvalApi.getEvalSuite(repoName, suiteName);

      if (isErrorResponse(result)) {
        errorNotification(
          result.title || 'Failed to Load Eval Suite',
          result.detail || `Unable to load eval suite "${suiteName}".`
        );
        throw new Error(result.detail || 'Failed to load eval suite');
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
   * Create or update eval suite
   * @param repoName - Repository name
   * @param suiteData - Eval suite data to save
   * @returns Saved eval suite data
   */
  static async saveEvalSuite(repoName: string, suiteData: EvalSuiteData): Promise<EvalSuiteData> {
    try {
      const result = await EvalApi.saveEvalSuite(repoName, suiteData);

      if (isErrorResponse(result)) {
        errorNotification(
          result.title || 'Failed to Save Eval Suite',
          result.detail || 'Unable to save eval suite. Changes may not be saved.'
        );
        throw new Error(result.detail || 'Failed to save eval suite');
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
        'Unable to connect to eval service. Changes may not be saved.'
      );
      throw error;
    }
  }

  /**
   * Delete eval suite
   * @param repoName - Repository name
   * @param suiteName - Eval suite name
   * @returns Success status
   */
  static async deleteEvalSuite(repoName: string, suiteName: string): Promise<boolean> {
    try {
      const result = await EvalApi.deleteEvalSuite(repoName, suiteName);

      if (isErrorResponse(result)) {
        errorNotification(
          result.title || 'Failed to Delete Eval Suite',
          result.detail || `Unable to delete eval suite "${suiteName}".`
        );
        throw new Error(result.detail || 'Failed to delete eval suite');
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
   * Execute eval suite or specific evals
   * @param repoName - Repository name
   * @param suiteName - Eval suite name
   * @param evalNames - Optional array of specific eval names to execute
   * @returns Eval suite execution results
   */
  static async executeEvalSuite(
    repoName: string,
    suiteName: string,
    evalNames?: string[]
  ): Promise<EvalSuiteExecutionResult> {
    try {
      const result = await EvalApi.executeEvalSuite(repoName, suiteName, evalNames);

      if (isErrorResponse(result)) {
        errorNotification(
          result.title || 'Eval Execution Failed',
          result.detail || `Unable to execute eval suite "${suiteName}".`
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
   * Execute single eval
   * @param repoName - Repository name
   * @param suiteName - Eval suite name
   * @param evalName - Eval name
   * @returns Eval execution result
   */
  static async executeSingleEval(
    repoName: string,
    suiteName: string,
    evalName: string
  ): Promise<EvalExecutionResult> {
    try {
      const result = await EvalApi.executeSingleEval(repoName, suiteName, evalName);

      if (isErrorResponse(result)) {
        errorNotification(
          result.title || 'Eval Execution Failed',
          result.detail || `Unable to execute eval "${evalName}".`
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
   * Get execution history for eval suite
   * @param repoName - Repository name
   * @param suiteName - Eval suite name
   * @param limit - Maximum number of executions to return
   * @returns List of execution results
   */
  static async getExecutionHistory(
    repoName: string,
    suiteName: string,
    limit: number = 10
  ): Promise<EvalSuiteExecutionResult[]> {
    try {
      const result = await EvalApi.getExecutionHistory(repoName, suiteName, limit);

      if (isErrorResponse(result)) {
        errorNotification(
          result.title || 'Failed to Load Execution History',
          result.detail || `Unable to load execution history for "${suiteName}".`
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
   * Get latest execution for eval suite
   * @param repoName - Repository name
   * @param suiteName - Eval suite name
   * @returns Latest execution result or null
   */
  static async getLatestExecution(
    repoName: string,
    suiteName: string
  ): Promise<EvalSuiteExecutionResult | null> {
    try {
      const result = await EvalApi.getLatestExecution(repoName, suiteName);

      if (isErrorResponse(result)) {
        errorNotification(
          result.title || 'Failed to Load Latest Execution',
          result.detail || `Unable to load latest execution for "${suiteName}".`
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