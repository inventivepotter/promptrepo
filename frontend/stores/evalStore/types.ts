/**
 * Types for Eval Store
 */
import type {
  EvalSuiteData,
  EvalSuiteSummary,
  EvalSuiteExecutionResult,
  EvalDefinition
} from '@/types/eval';

/**
 * Eval Store State
 */
export interface EvalState {
  /** List of eval suite summaries */
  evalSuites: EvalSuiteSummary[];
  /** Currently selected eval suite */
  currentSuite: EvalSuiteData | null;
  /** Current execution result */
  currentExecution: EvalSuiteExecutionResult | null;
  /** Execution history for current suite */
  executionHistory: EvalSuiteExecutionResult[];
  /** Currently editing eval in the editor */
  editingEval: EvalDefinition | null;
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
  // Suite management actions
  /** Fetch all eval suites for a repository */
  fetchEvalSuites: (repoName: string) => Promise<void>;
  /** Fetch specific eval suite */
  fetchEvalSuite: (repoName: string, suiteName: string) => Promise<void>;
  /** Save eval suite (create or update) */
  saveEvalSuite: (repoName: string, suiteData: EvalSuiteData) => Promise<void>;
  /** Delete eval suite */
  deleteEvalSuite: (repoName: string, suiteName: string) => Promise<void>;
  
  // Execution actions
  /** Execute entire eval suite or specific evals */
  executeEvalSuite: (repoName: string, suiteName: string, evalNames?: string[]) => Promise<void>;
  /** Execute single eval */
  executeSingleEval: (repoName: string, suiteName: string, evalName: string) => Promise<void>;
  /** Fetch execution history */
  fetchExecutionHistory: (repoName: string, suiteName: string, limit?: number) => Promise<void>;
  /** Fetch latest execution */
  fetchLatestExecution: (repoName: string, suiteName: string) => Promise<void>;
  
  // Local state mutations
  /** Set currently selected eval suite */
  setCurrentSuite: (suite: EvalSuiteData | null) => void;
  /** Set current execution result */
  setCurrentExecution: (execution: EvalSuiteExecutionResult | null) => void;
  /** Set currently editing eval */
  setEditingEval: (evalItem: EvalDefinition | null) => void;
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