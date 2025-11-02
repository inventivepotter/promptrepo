import httpClient from '@/lib/httpClient';
import type { OpenApiResponse } from '@/types/OpenApiResponse';
import type { components } from '@/types/generated/api';

// Type aliases from generated types
type EvalMeta = components['schemas']['EvalMeta'];
type EvalData = components['schemas']['EvalData'];
type EvalExecutionResult = components['schemas']['EvalExecutionResult'];
type TestExecutionResult = components['schemas']['TestExecutionResult'];
type MetricsMetadataResponse = Record<string, components['schemas']['MetricMetadataModel']>;

/**
 * Eval API client
 * All methods return OpenAPI-formatted responses
 */
export default class EvalApi {
  /**
   * Get metrics metadata
   * @returns OpenAPI response with metrics metadata
   */
  static async getMetricsMetadata(): Promise<OpenApiResponse<MetricsMetadataResponse>> {
    return httpClient.get<MetricsMetadataResponse>('/api/v0/evals/metrics/metadata');
  }

  /**
   * List all evals in a repository
   * @param repoName - Repository name
   * @returns OpenAPI response with list of eval metadata
   */
  static async listEvals(repoName: string): Promise<OpenApiResponse<EvalMeta[]>> {
    return httpClient.get<EvalMeta[]>(`/api/v0/evals/?repo_name=${encodeURIComponent(repoName)}`);
  }

  /**
   * Get specific eval definition
   * @param repoName - Repository name
   * @param filePath - Eval file path
   * @returns OpenAPI response with eval metadata
   */
  static async getEval(repoName: string, filePath: string): Promise<OpenApiResponse<EvalMeta>> {
    const encodedRepoName = btoa(repoName);
    const encodedFilePath = btoa(filePath);
    
    return httpClient.get<EvalMeta>(
      `/api/v0/evals/${encodedRepoName}/${encodedFilePath}`
    );
  }

  /**
   * Create or update eval
   * @param repoName - Repository name
   * @param filePath - Eval file path (use 'new' for creating new eval)
   * @param evalData - Eval data to save
   * @returns OpenAPI response with saved eval
   */
  static async saveEval(repoName: string, filePath: string, evalData: EvalData): Promise<OpenApiResponse<EvalMeta>> {
    const encodedRepoName = btoa(repoName);
    const encodedFilePath = filePath === 'new' ? 'new' : btoa(filePath);
    
    return httpClient.post<EvalMeta>(
      `/api/v0/evals/${encodedRepoName}/${encodedFilePath}`,
      evalData
    );
  }

  /**
   * Delete eval
   * @param repoName - Repository name
   * @param filePath - Eval file path
   * @returns OpenAPI response with deletion confirmation
   */
  static async deleteEval(repoName: string, filePath: string): Promise<OpenApiResponse<{ deleted: boolean; file_path: string }>> {
    const encodedRepoName = btoa(repoName);
    const encodedFilePath = btoa(filePath);
    
    return httpClient.delete<{ deleted: boolean; file_path: string }>(
      `/api/v0/evals/${encodedRepoName}/${encodedFilePath}`
    );
  }

  /**
   * Execute eval or specific tests
   * @param repoName - Repository name
   * @param evalName - Eval name
   * @param testNames - Optional array of specific test names to execute
   * @returns OpenAPI response with execution results
   */
  static async executeEval(
    repoName: string,
    evalName: string,
    testNames?: string[]
  ): Promise<OpenApiResponse<EvalExecutionResult>> {
    return httpClient.post<EvalExecutionResult>(
      `/api/v0/evals/executions/${encodeURIComponent(evalName)}/execute?repo_name=${encodeURIComponent(repoName)}`,
      { test_names: testNames }
    );
  }

  /**
   * Execute single test
   * @param repoName - Repository name
   * @param evalName - Eval name
   * @param testName - Test name
   * @returns OpenAPI response with test execution result
   */
  static async executeSingleTest(
    repoName: string,
    evalName: string,
    testName: string
  ): Promise<OpenApiResponse<TestExecutionResult>> {
    return httpClient.post<TestExecutionResult>(
      `/api/v0/evals/executions/${encodeURIComponent(evalName)}/tests/${encodeURIComponent(testName)}/execute?repo_name=${encodeURIComponent(repoName)}`
    );
  }

  /**
   * Get execution history for eval
   * @param repoName - Repository name
   * @param evalName - Eval name
   * @param limit - Maximum number of executions to return (default: 10)
   * @returns OpenAPI response with execution history
   */
  static async getExecutionHistory(
    repoName: string,
    evalName: string,
    limit: number = 10
  ): Promise<OpenApiResponse<EvalExecutionResult[]>> {
    return httpClient.get<EvalExecutionResult[]>(
      `/api/v0/evals/executions/${encodeURIComponent(evalName)}/executions?repo_name=${encodeURIComponent(repoName)}&limit=${limit}`
    );
  }

  /**
   * Get latest execution for eval
   * @param repoName - Repository name
   * @param evalName - Eval name
   * @returns OpenAPI response with latest execution or null
   */
  static async getLatestExecution(
    repoName: string,
    evalName: string
  ): Promise<OpenApiResponse<EvalExecutionResult | null>> {
    return httpClient.get<EvalExecutionResult | null>(
      `/api/v0/evals/executions/${encodeURIComponent(evalName)}/executions/latest?repo_name=${encodeURIComponent(repoName)}`
    );
  }
}