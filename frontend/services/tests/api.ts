import httpClient from '@/lib/httpClient';
import type { OpenApiResponse } from '@/types/OpenApiResponse';
import type {
  TestSuiteData,
  TestSuiteSummary,
  TestSuiteExecutionResult,
  UnitTestExecutionResult,
  MetricsMetadataResponse
} from '@/types/test';

/**
 * Test API client
 * All methods return OpenAPI-formatted responses
 */
export default class TestApi {
  /**
   * Get metrics metadata
   * @returns OpenAPI response with metrics metadata
   */
  static async getMetricsMetadata(): Promise<OpenApiResponse<MetricsMetadataResponse>> {
    return httpClient.get<MetricsMetadataResponse>('/api/v0/tests/metrics/metadata');
  }

  /**
   * List all test suites in a repository
   * @param repoName - Repository name
   * @returns OpenAPI response with list of test suite summaries
   */
  static async listTestSuites(repoName: string): Promise<OpenApiResponse<TestSuiteSummary[]>> {
    return httpClient.get<TestSuiteSummary[]>(`/api/v0/tests/suites?repo_name=${encodeURIComponent(repoName)}`);
  }

  /**
   * Get specific test suite definition
   * @param repoName - Repository name
   * @param suiteName - Test suite name
   * @returns OpenAPI response with test suite data
   */
  static async getTestSuite(repoName: string, suiteName: string): Promise<OpenApiResponse<TestSuiteData>> {
    return httpClient.get<TestSuiteData>(
      `/api/v0/tests/suites/${encodeURIComponent(suiteName)}?repo_name=${encodeURIComponent(repoName)}`
    );
  }

  /**
   * Create or update test suite
   * @param repoName - Repository name
   * @param suiteData - Test suite data to save
   * @returns OpenAPI response with saved test suite
   */
  static async saveTestSuite(repoName: string, suiteData: TestSuiteData): Promise<OpenApiResponse<TestSuiteData>> {
    return httpClient.post<TestSuiteData>(
      `/api/v0/tests/suites?repo_name=${encodeURIComponent(repoName)}`,
      suiteData
    );
  }

  /**
   * Delete test suite
   * @param repoName - Repository name
   * @param suiteName - Test suite name
   * @returns OpenAPI response with deletion confirmation
   */
  static async deleteTestSuite(repoName: string, suiteName: string): Promise<OpenApiResponse<{ deleted: boolean; suite_name: string }>> {
    return httpClient.delete<{ deleted: boolean; suite_name: string }>(
      `/api/v0/tests/suites/${encodeURIComponent(suiteName)}?repo_name=${encodeURIComponent(repoName)}`
    );
  }

  /**
   * Execute test suite or specific tests
   * @param repoName - Repository name
   * @param suiteName - Test suite name
   * @param testNames - Optional array of specific test names to execute
   * @returns OpenAPI response with execution results
   */
  static async executeTestSuite(
    repoName: string,
    suiteName: string,
    testNames?: string[]
  ): Promise<OpenApiResponse<TestSuiteExecutionResult>> {
    return httpClient.post<TestSuiteExecutionResult>(
      `/api/v0/tests/suites/${encodeURIComponent(suiteName)}/execute?repo_name=${encodeURIComponent(repoName)}`,
      { test_names: testNames }
    );
  }

  /**
   * Execute single test
   * @param repoName - Repository name
   * @param suiteName - Test suite name
   * @param testName - Test name
   * @returns OpenAPI response with test execution result
   */
  static async executeSingleTest(
    repoName: string,
    suiteName: string,
    testName: string
  ): Promise<OpenApiResponse<UnitTestExecutionResult>> {
    return httpClient.post<UnitTestExecutionResult>(
      `/api/v0/tests/suites/${encodeURIComponent(suiteName)}/tests/${encodeURIComponent(testName)}/execute?repo_name=${encodeURIComponent(repoName)}`
    );
  }

  /**
   * Get execution history for test suite
   * @param repoName - Repository name
   * @param suiteName - Test suite name
   * @param limit - Maximum number of executions to return (default: 10)
   * @returns OpenAPI response with execution history
   */
  static async getExecutionHistory(
    repoName: string,
    suiteName: string,
    limit: number = 10
  ): Promise<OpenApiResponse<TestSuiteExecutionResult[]>> {
    return httpClient.get<TestSuiteExecutionResult[]>(
      `/api/v0/tests/suites/${encodeURIComponent(suiteName)}/executions?repo_name=${encodeURIComponent(repoName)}&limit=${limit}`
    );
  }

  /**
   * Get latest execution for test suite
   * @param repoName - Repository name
   * @param suiteName - Test suite name
   * @returns OpenAPI response with latest execution or null
   */
  static async getLatestExecution(
    repoName: string,
    suiteName: string
  ): Promise<OpenApiResponse<TestSuiteExecutionResult | null>> {
    return httpClient.get<TestSuiteExecutionResult | null>(
      `/api/v0/tests/suites/${encodeURIComponent(suiteName)}/executions/latest?repo_name=${encodeURIComponent(repoName)}`
    );
  }
}