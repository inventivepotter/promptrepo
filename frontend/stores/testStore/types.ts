/**
 * Types for Test Store
 */
import type {
  TestSuiteData,
  TestSuiteSummary,
  TestSuiteExecutionResult,
  UnitTestExecutionResult
} from '@/types/test';

/**
 * Test Store State
 */
export interface TestState {
  /** List of test suite summaries */
  testSuites: TestSuiteSummary[];
  /** Currently selected test suite */
  currentSuite: TestSuiteData | null;
  /** Current execution result */
  currentExecution: TestSuiteExecutionResult | null;
  /** Execution history for current suite */
  executionHistory: TestSuiteExecutionResult[];
  /** Loading state */
  isLoading: boolean;
  /** Error message */
  error: string | null;
  /** Currently selected repository */
  selectedRepo: string;
}

/**
 * Test Store Actions
 */
export interface TestActions {
  // Suite management actions
  /** Fetch all test suites for a repository */
  fetchTestSuites: (repoName: string) => Promise<void>;
  /** Fetch specific test suite */
  fetchTestSuite: (repoName: string, suiteName: string) => Promise<void>;
  /** Save test suite (create or update) */
  saveTestSuite: (repoName: string, suiteData: TestSuiteData) => Promise<void>;
  /** Delete test suite */
  deleteTestSuite: (repoName: string, suiteName: string) => Promise<void>;
  
  // Execution actions
  /** Execute entire test suite or specific tests */
  executeTestSuite: (repoName: string, suiteName: string, testNames?: string[]) => Promise<void>;
  /** Execute single test */
  executeSingleTest: (repoName: string, suiteName: string, testName: string) => Promise<void>;
  /** Fetch execution history */
  fetchExecutionHistory: (repoName: string, suiteName: string, limit?: number) => Promise<void>;
  /** Fetch latest execution */
  fetchLatestExecution: (repoName: string, suiteName: string) => Promise<void>;
  
  // Local state mutations
  /** Set currently selected test suite */
  setCurrentSuite: (suite: TestSuiteData | null) => void;
  /** Set current execution result */
  setCurrentExecution: (execution: TestSuiteExecutionResult | null) => void;
  /** Set loading state */
  setLoading: (loading: boolean) => void;
  /** Set error state */
  setError: (error: string | null) => void;
  /** Set selected repository */
  setSelectedRepo: (repoName: string) => void;
  /** Clear all test data */
  clearTestData: () => void;
}

/**
 * Combined Test Store type
 */
export type TestStore = TestState & TestActions;