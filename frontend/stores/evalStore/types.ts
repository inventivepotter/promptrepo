/**
 * Types for Eval Store
 */
import type {
  EvalData,
  EvalSummary,
  EvalMeta,
  EvalExecutionResult,
  TestDefinition
} from '@/types/eval';

/**
 * Eval Store State
 */
export interface EvalState {
  /** List of eval summaries */
  evals: EvalSummary[];
  /** Currently selected eval */
  currentEval: EvalData | null;
  /** Current execution result */
  currentExecution: EvalExecutionResult | null;
  /** Execution history for current eval */
  executionHistory: EvalExecutionResult[];
  /** Currently editing test in the editor */
  editingTest: TestDefinition | null;
  /** Loading state */
  isLoading: boolean;
  /** Error message */
  error: string | null;
  /** Currently selected repository */
  selectedRepo: string;
}

/**
 * Eval Store Actions
 */
export interface EvalActions {
  // Eval management actions
  /** Fetch all evals for a repository */
  fetchEvals: (repoName: string) => Promise<void>;
  /** Fetch specific eval */
  fetchEval: (repoName: string, filePath: string) => Promise<void>;
  /** Save eval (create or update) - returns saved EvalMeta */
  saveEval: (repoName: string, evalData: EvalData, filePath?: string) => Promise<EvalMeta>;
  /** Delete eval */
  deleteEval: (repoName: string, filePath: string) => Promise<void>;

  // Execution actions
  /** Execute entire eval or specific tests */
  executeEval: (repoName: string, filePath: string, testNames?: string[]) => Promise<void>;
  /** Execute single test */
  executeSingleTest: (repoName: string, filePath: string, testName: string) => Promise<void>;
  /** Fetch execution history */
  fetchExecutionHistory: (repoName: string, filePath: string, limit?: number) => Promise<void>;
  /** Fetch latest execution */
  fetchLatestExecution: (repoName: string, filePath: string) => Promise<void>;

  // Local state mutations
  /** Set currently selected eval */
  setCurrentEval: (evalData: EvalData | null) => void;
  /** Set current execution result */
  setCurrentExecution: (execution: EvalExecutionResult | null) => void;
  /** Set currently editing test */
  setEditingTest: (testItem: TestDefinition | null) => void;
  /** Set loading state */
  setLoading: (loading: boolean) => void;
  /** Set error state */
  setError: (error: string | null) => void;
  /** Set selected repository */
  setSelectedRepo: (repoName: string) => void;
  /** Clear all eval data */
  clearEvalData: () => void;
}

/**
 * Combined Eval Store type
 */
export type EvalStore = EvalState & EvalActions;