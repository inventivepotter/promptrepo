/**
 * Actions for Eval Store
 */
import type { StateCreator } from 'zustand';
import { EvalService } from '@/services/evals/evalService';
import { handleStoreError } from '@/lib/zustand';
import type { EvalStore, EvalActions } from './types';
import type { EvalData, EvalExecutionResult } from '@/types/eval';

export const createEvalActions: StateCreator<
  EvalStore,
  [['zustand/devtools', never], ['zustand/immer', never]],
  [],
  EvalActions
> = (set, get) => ({
  // Eval management actions
  fetchEvals: async (repoName: string) => {
    set({ isLoading: true, error: null });
    try {
      const evals = await EvalService.listEvals(repoName);
      set({ evals, isLoading: false, selectedRepo: repoName });
    } catch (error) {
      const storeError = handleStoreError(error, 'fetchEvals');
      set({ error: storeError.message, isLoading: false });
    }
  },

  fetchEval: async (repoName: string, evalName: string) => {
    set({ isLoading: true, error: null });
    try {
      const evalData = await EvalService.getEval(repoName, evalName);
      set({ currentEval: evalData, isLoading: false });
    } catch (error) {
      const storeError = handleStoreError(error, 'fetchEval');
      set({ error: storeError.message, isLoading: false });
    }
  },

  saveEval: async (repoName: string, evalData: EvalData) => {
    set({ isLoading: true, error: null });
    try {
      const savedEval = await EvalService.saveEval(repoName, evalData);
      set({ currentEval: savedEval, isLoading: false });
      
      // Refresh evals list
      await get().fetchEvals(repoName);
    } catch (error) {
      const storeError = handleStoreError(error, 'saveEval');
      set({ error: storeError.message, isLoading: false });
    }
  },

  deleteEval: async (repoName: string, evalName: string) => {
    set({ isLoading: true, error: null });
    try {
      await EvalService.deleteEval(repoName, evalName);
      set({ currentEval: null, isLoading: false });
      
      // Refresh evals list
      await get().fetchEvals(repoName);
    } catch (error) {
      const storeError = handleStoreError(error, 'deleteEval');
      set({ error: storeError.message, isLoading: false });
    }
  },

  // Execution actions
  executeEval: async (repoName: string, evalName: string, testNames?: string[]) => {
    set({ isLoading: true, error: null });
    try {
      const executionResult = await EvalService.executeEval(repoName, evalName, testNames);
      set({ currentExecution: executionResult, isLoading: false });
      
      // Refresh execution history
      await get().fetchExecutionHistory(repoName, evalName);
    } catch (error) {
      const storeError = handleStoreError(error, 'executeEval');
      set({ error: storeError.message, isLoading: false });
    }
  },

  executeSingleTest: async (repoName: string, evalName: string, testName: string) => {
    set({ isLoading: true, error: null });
    try {
      const testResult = await EvalService.executeSingleTest(repoName, evalName, testName);
      
      // Create an eval execution result with single test
      const evalExecution: EvalExecutionResult = {
        eval_name: evalName,
        test_results: [testResult],
        total_tests: 1,
        passed_tests: testResult.overall_passed ? 1 : 0,
        failed_tests: testResult.overall_passed ? 0 : 1,
        total_execution_time_ms: testResult.actual_test_fields.execution_time_ms || 0,
        executed_at: testResult.executed_at,
      };
      
      set({ currentExecution: evalExecution, isLoading: false });
    } catch (error) {
      const storeError = handleStoreError(error, 'executeSingleTest');
      set({ error: storeError.message, isLoading: false });
    }
  },

  fetchExecutionHistory: async (repoName: string, evalName: string, limit: number = 10) => {
    set({ isLoading: true, error: null });
    try {
      const history = await EvalService.getExecutionHistory(repoName, evalName, limit);
      set({ executionHistory: history, isLoading: false });
    } catch (error) {
      const storeError = handleStoreError(error, 'fetchExecutionHistory');
      set({ error: storeError.message, isLoading: false });
    }
  },

  fetchLatestExecution: async (repoName: string, evalName: string) => {
    set({ isLoading: true, error: null });
    try {
      const latestExecution = await EvalService.getLatestExecution(repoName, evalName);
      set({ currentExecution: latestExecution, isLoading: false });
    } catch (error) {
      const storeError = handleStoreError(error, 'fetchLatestExecution');
      set({ error: storeError.message, isLoading: false });
    }
  },

  // Local state mutations
  setCurrentEval: (evalData: EvalData | null) => {
    set({ currentEval: evalData });
  },

  setCurrentExecution: (execution: EvalExecutionResult | null) => {
    set({ currentExecution: execution });
  },

  setEditingTest: (testItem) => {
    set({ editingTest: testItem });
  },

  setLoading: (loading: boolean) => {
    set({ isLoading: loading });
  },

  setError: (error: string | null) => {
    set({ error });
  },

  setSelectedRepo: (repoName: string) => {
    set({ selectedRepo: repoName });
  },

  clearEvalData: () => {
    set({
      evals: [],
      currentEval: null,
      currentExecution: null,
      executionHistory: [],
      editingTest: null,
      error: null,
    });
  },
});