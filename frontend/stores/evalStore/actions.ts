/**
 * Actions for Eval Store
 */
import type { StateCreator } from 'zustand';
import { EvalService } from '@/services/evals/evalService';
import { handleStoreError } from '@/lib/zustand';
import type { EvalStore, EvalActions } from './types';
import type { EvalSuiteData, EvalSuiteExecutionResult } from '@/types/eval';

export const createEvalActions: StateCreator<
  EvalStore,
  [['zustand/devtools', never], ['zustand/immer', never]],
  [],
  EvalActions
> = (set, get) => ({
  // Suite management actions
  fetchEvalSuites: async (repoName: string) => {
    set({ isLoading: true, error: null });
    try {
      const evalSuites = await EvalService.listEvalSuites(repoName);
      set({ evalSuites, isLoading: false, selectedRepo: repoName });
    } catch (error) {
      const storeError = handleStoreError(error, 'fetchEvalSuites');
      set({ error: storeError.message, isLoading: false });
    }
  },

  fetchEvalSuite: async (repoName: string, suiteName: string) => {
    set({ isLoading: true, error: null });
    try {
      const suiteData = await EvalService.getEvalSuite(repoName, suiteName);
      set({ currentSuite: suiteData, isLoading: false });
    } catch (error) {
      const storeError = handleStoreError(error, 'fetchEvalSuite');
      set({ error: storeError.message, isLoading: false });
    }
  },

  saveEvalSuite: async (repoName: string, suiteData: EvalSuiteData) => {
    set({ isLoading: true, error: null });
    try {
      const savedSuite = await EvalService.saveEvalSuite(repoName, suiteData);
      set({ currentSuite: savedSuite, isLoading: false });
      
      // Refresh eval suites list
      await get().fetchEvalSuites(repoName);
    } catch (error) {
      const storeError = handleStoreError(error, 'saveEvalSuite');
      set({ error: storeError.message, isLoading: false });
    }
  },

  deleteEvalSuite: async (repoName: string, suiteName: string) => {
    set({ isLoading: true, error: null });
    try {
      await EvalService.deleteEvalSuite(repoName, suiteName);
      set({ currentSuite: null, isLoading: false });
      
      // Refresh eval suites list
      await get().fetchEvalSuites(repoName);
    } catch (error) {
      const storeError = handleStoreError(error, 'deleteEvalSuite');
      set({ error: storeError.message, isLoading: false });
    }
  },

  // Execution actions
  executeEvalSuite: async (repoName: string, suiteName: string, evalNames?: string[]) => {
    set({ isLoading: true, error: null });
    try {
      const executionResult = await EvalService.executeEvalSuite(repoName, suiteName, evalNames);
      set({ currentExecution: executionResult, isLoading: false });
      
      // Refresh execution history
      await get().fetchExecutionHistory(repoName, suiteName);
    } catch (error) {
      const storeError = handleStoreError(error, 'executeEvalSuite');
      set({ error: storeError.message, isLoading: false });
    }
  },

  executeSingleEval: async (repoName: string, suiteName: string, evalName: string) => {
    set({ isLoading: true, error: null });
    try {
      const evalResult = await EvalService.executeSingleEval(repoName, suiteName, evalName);
      
      // Create a suite execution result with single eval
      const suiteExecution: EvalSuiteExecutionResult = {
        suite_name: suiteName,
        eval_results: [evalResult],
        total_evals: 1,
        passed_evals: evalResult.overall_passed ? 1 : 0,
        failed_evals: evalResult.overall_passed ? 0 : 1,
        total_execution_time_ms: evalResult.actual_evaluation_fields.execution_time_ms || 0,
        executed_at: evalResult.executed_at,
      };
      
      set({ currentExecution: suiteExecution, isLoading: false });
    } catch (error) {
      const storeError = handleStoreError(error, 'executeSingleEval');
      set({ error: storeError.message, isLoading: false });
    }
  },

  fetchExecutionHistory: async (repoName: string, suiteName: string, limit: number = 10) => {
    set({ isLoading: true, error: null });
    try {
      const history = await EvalService.getExecutionHistory(repoName, suiteName, limit);
      set({ executionHistory: history, isLoading: false });
    } catch (error) {
      const storeError = handleStoreError(error, 'fetchExecutionHistory');
      set({ error: storeError.message, isLoading: false });
    }
  },

  fetchLatestExecution: async (repoName: string, suiteName: string) => {
    set({ isLoading: true, error: null });
    try {
      const latestExecution = await EvalService.getLatestExecution(repoName, suiteName);
      set({ currentExecution: latestExecution, isLoading: false });
    } catch (error) {
      const storeError = handleStoreError(error, 'fetchLatestExecution');
      set({ error: storeError.message, isLoading: false });
    }
  },

  // Local state mutations
  setCurrentSuite: (suite: EvalSuiteData | null) => {
    set({ currentSuite: suite });
  },

  setCurrentExecution: (execution: EvalSuiteExecutionResult | null) => {
    set({ currentExecution: execution });
  },

  setEditingEval: (evalItem) => {
    set({ editingEval: evalItem });
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
      evalSuites: [],
      currentSuite: null,
      currentExecution: null,
      executionHistory: [],
      editingEval: null,
      error: null,
    });
  },
});