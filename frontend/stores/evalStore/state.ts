/**
 * Initial state for Eval Store
 */
import type { EvalState } from './types';

export const initialEvalState: EvalState = {
  evalSuites: [],
  currentSuite: null,
  currentExecution: null,
  executionHistory: [],
  editingEval: null,
  isLoading: false,
  error: null,
  selectedRepo: '',
};