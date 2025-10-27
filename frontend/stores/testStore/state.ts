/**
 * Initial state for Test Store
 */
import type { TestState } from './types';

export const initialTestState: TestState = {
  testSuites: [],
  currentSuite: null,
  currentExecution: null,
  executionHistory: [],
  isLoading: false,
  error: null,
  selectedRepo: '',
};