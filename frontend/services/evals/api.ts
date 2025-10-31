import httpClient from '@/lib/httpClient';
import type { OpenApiResponse } from '@/types/OpenApiResponse';
import type {
  EvalSuiteData,
  EvalSuiteSummary,
  EvalSuiteExecutionResult,
  EvalExecutionResult,
  MetricsMetadataResponse
} from '@/types/eval';

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
   * List all eval suites in a repository
   * @param repoName - Repository name
   * @returns OpenAPI response with list of eval suite summaries
   */
  static async listEvalSuites(repoName: string): Promise<OpenApiResponse<EvalSuiteSummary[]>> {
    return httpClient.get<EvalSuiteSummary[]>(`/api/v0/evals/suites?repo_name=${encodeURIComponent(repoName)}`);
  }

  /**
   * Get specific eval suite definition
   * @param repoName - Repository name
   * @param suiteName - Eval suite name
   * @returns OpenAPI response with eval suite data
   */
  static async getEvalSuite(repoName: string, suiteName: string): Promise<OpenApiResponse<EvalSuiteData>> {
    return httpClient.get<EvalSuiteData>(
      `/api/v0/evals/suites/${encodeURIComponent(suiteName)}?repo_name=${encodeURIComponent(repoName)}`
    );
  }

  /**
   * Create or update eval suite
   * @param repoName - Repository name
   * @param suiteData - Eval suite data to save
   * @returns OpenAPI response with saved eval suite
   */
  static async saveEvalSuite(repoName: string, suiteData: EvalSuiteData): Promise<OpenApiResponse<EvalSuiteData>> {
    return httpClient.post<EvalSuiteData>(
      `/api/v0/evals/suites?repo_name=${encodeURIComponent(repoName)}`,
      suiteData
    );
  }

  /**
   * Delete eval suite
   * @param repoName - Repository name
   * @param suiteName - Eval suite name
   * @returns OpenAPI response with deletion confirmation
   */
  static async deleteEvalSuite(repoName: string, suiteName: string): Promise<OpenApiResponse<{ deleted: boolean; suite_name: string }>> {
    return httpClient.delete<{ deleted: boolean; suite_name: string }>(
      `/api/v0/evals/suites/${encodeURIComponent(suiteName)}?repo_name=${encodeURIComponent(repoName)}`
    );
  }

  /**
   * Execute eval suite or specific evals
   * @param repoName - Repository name
   * @param suiteName - Eval suite name
   * @param evalNames - Optional array of specific eval names to execute
   * @returns OpenAPI response with execution results
   */
  static async executeEvalSuite(
    repoName: string,
    suiteName: string,
    evalNames?: string[]
  ): Promise<OpenApiResponse<EvalSuiteExecutionResult>> {
    return httpClient.post<EvalSuiteExecutionResult>(
      `/api/v0/evals/suites/${encodeURIComponent(suiteName)}/execute?repo_name=${encodeURIComponent(repoName)}`,
      { eval_names: evalNames }
    );
  }

  /**
   * Execute single eval
   * @param repoName - Repository name
   * @param suiteName - Eval suite name
   * @param evalName - Eval name
   * @returns OpenAPI response with eval execution result
   */
  static async executeSingleEval(
    repoName: string,
    suiteName: string,
    evalName: string
  ): Promise<OpenApiResponse<EvalExecutionResult>> {
    return httpClient.post<EvalExecutionResult>(
      `/api/v0/evals/suites/${encodeURIComponent(suiteName)}/evals/${encodeURIComponent(evalName)}/execute?repo_name=${encodeURIComponent(repoName)}`
    );
  }

  /**
   * Get execution history for eval suite
   * @param repoName - Repository name
   * @param suiteName - Eval suite name
   * @param limit - Maximum number of executions to return (default: 10)
   * @returns OpenAPI response with execution history
   */
  static async getExecutionHistory(
    repoName: string,
    suiteName: string,
    limit: number = 10
  ): Promise<OpenApiResponse<EvalSuiteExecutionResult[]>> {
    return httpClient.get<EvalSuiteExecutionResult[]>(
      `/api/v0/evals/suites/${encodeURIComponent(suiteName)}/executions?repo_name=${encodeURIComponent(repoName)}&limit=${limit}`
    );
  }

  /**
   * Get latest execution for eval suite
   * @param repoName - Repository name
   * @param suiteName - Eval suite name
   * @returns OpenAPI response with latest execution or null
   */
  static async getLatestExecution(
    repoName: string,
    suiteName: string
  ): Promise<OpenApiResponse<EvalSuiteExecutionResult | null>> {
    return httpClient.get<EvalSuiteExecutionResult | null>(
      `/api/v0/evals/suites/${encodeURIComponent(suiteName)}/executions/latest?repo_name=${encodeURIComponent(repoName)}`
    );
  }
}