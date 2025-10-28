import TestApi from './api';
import { errorNotification } from '@/lib/notifications';
import { isStandardResponse, isErrorResponse } from '@/types/OpenApiResponse';
import type {
  TestSuiteData,
  TestSuiteSummary,
  TestSuiteExecutionResult,
  UnitTestExecutionResult
} from '@/types/test';

/**
 * Test service for DeepEval test management
 * Handles API calls with proper error handling and notifications
 */
export class TestService {
  /**
   * List all test suites in a repository
   * @param repoName - Repository name
   * @returns List of test suite summaries
   */
  static async listTestSuites(repoName: string): Promise<TestSuiteSummary[]> {
    try {
      const result = await TestApi.listTestSuites(repoName);

      if (isErrorResponse(result)) {
        errorNotification(
          result.title || 'Failed to Load Test Suites',
          result.detail || 'Unable to load test suites from server.'
        );
        throw new Error(result.detail || 'Failed to load test suites');
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
          'Unable to connect to test service.'
        );
      }
      throw error;
    }
  }

  /**
   * Get specific test suite definition
   * @param repoName - Repository name
   * @param suiteName - Test suite name
   * @returns Test suite data
   */
  static async getTestSuite(repoName: string, suiteName: string): Promise<TestSuiteData> {
    try {
      const result = await TestApi.getTestSuite(repoName, suiteName);

      if (isErrorResponse(result)) {
        errorNotification(
          result.title || 'Failed to Load Test Suite',
          result.detail || `Unable to load test suite "${suiteName}".`
        );
        throw new Error(result.detail || 'Failed to load test suite');
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
        'Unable to connect to test service.'
      );
      throw error;
    }
  }

  /**
   * Create or update test suite
   * @param repoName - Repository name
   * @param suiteData - Test suite data to save
   * @returns Saved test suite data
   */
  static async saveTestSuite(repoName: string, suiteData: TestSuiteData): Promise<TestSuiteData> {
    try {
      const result = await TestApi.saveTestSuite(repoName, suiteData);

      if (isErrorResponse(result)) {
        errorNotification(
          result.title || 'Failed to Save Test Suite',
          result.detail || 'Unable to save test suite. Changes may not be saved.'
        );
        throw new Error(result.detail || 'Failed to save test suite');
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
        'Unable to connect to test service. Changes may not be saved.'
      );
      throw error;
    }
  }

  /**
   * Delete test suite
   * @param repoName - Repository name
   * @param suiteName - Test suite name
   * @returns Success status
   */
  static async deleteTestSuite(repoName: string, suiteName: string): Promise<boolean> {
    try {
      const result = await TestApi.deleteTestSuite(repoName, suiteName);

      if (isErrorResponse(result)) {
        errorNotification(
          result.title || 'Failed to Delete Test Suite',
          result.detail || `Unable to delete test suite "${suiteName}".`
        );
        throw new Error(result.detail || 'Failed to delete test suite');
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
        'Unable to connect to test service.'
      );
      throw error;
    }
  }

  /**
   * Execute test suite or specific tests
   * @param repoName - Repository name
   * @param suiteName - Test suite name
   * @param testNames - Optional array of specific test names to execute
   * @returns Test suite execution results
   */
  static async executeTestSuite(
    repoName: string,
    suiteName: string,
    testNames?: string[]
  ): Promise<TestSuiteExecutionResult> {
    try {
      const result = await TestApi.executeTestSuite(repoName, suiteName, testNames);

      if (isErrorResponse(result)) {
        errorNotification(
          result.title || 'Test Execution Failed',
          result.detail || `Unable to execute test suite "${suiteName}".`
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
        'Unable to connect to test execution service.'
      );
      throw error;
    }
  }

  /**
   * Execute single test
   * @param repoName - Repository name
   * @param suiteName - Test suite name
   * @param testName - Test name
   * @returns Unit test execution result
   */
  static async executeSingleTest(
    repoName: string,
    suiteName: string,
    testName: string
  ): Promise<UnitTestExecutionResult> {
    try {
      const result = await TestApi.executeSingleTest(repoName, suiteName, testName);

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
        'Unable to connect to test execution service.'
      );
      throw error;
    }
  }

  /**
   * Get execution history for test suite
   * @param repoName - Repository name
   * @param suiteName - Test suite name
   * @param limit - Maximum number of executions to return
   * @returns List of execution results
   */
  static async getExecutionHistory(
    repoName: string,
    suiteName: string,
    limit: number = 10
  ): Promise<TestSuiteExecutionResult[]> {
    try {
      const result = await TestApi.getExecutionHistory(repoName, suiteName, limit);

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
        'Unable to connect to test service.'
      );
      throw error;
    }
  }

  /**
   * Get latest execution for test suite
   * @param repoName - Repository name
   * @param suiteName - Test suite name
   * @returns Latest execution result or null
   */
  static async getLatestExecution(
    repoName: string,
    suiteName: string
  ): Promise<TestSuiteExecutionResult | null> {
    try {
      const result = await TestApi.getLatestExecution(repoName, suiteName);

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
        'Unable to connect to test service.'
      );
      throw error;
    }
  }
}