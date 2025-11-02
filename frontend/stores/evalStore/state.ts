/**
 * Initial state for Eval Store
 */
import type { EvalState } from './types';

export const initialEvalState: EvalState = {
  evals: [],
  currentEval: null,
  currentExecution: null,
  executionHistory: [],
  editingTest: null,
  isLoading: false,
  error: null,
  selectedRepo: '',
};