/**
 * Actions for Test Store
 */
import type { StateCreator } from 'zustand';
import { TestService } from '@/services/tests/testService';
import { handleStoreError } from '@/lib/zustand';
import type { TestStore, TestActions } from './types';
import type { TestSuiteData, TestSuiteExecutionResult } from '@/types/test';

export const createTestActions: StateCreator<
  TestStore,
  [['zustand/devtools', never], ['zustand/immer', never]],
  [],
  TestActions
> = (set, get) => ({
  // Suite management actions
  fetchTestSuites: async (repoName: string) => {
    set({ isLoading: true, error: null });
    try {
      const testSuites = await TestService.listTestSuites(repoName);
      set({ testSuites, isLoading: false, selectedRepo: repoName });
    } catch (error) {
      const storeError = handleStoreError(error, 'fetchTestSuites');
      set({ error: storeError.message, isLoading: false });
    }
  },

  fetchTestSuite: async (repoName: string, suiteName: string) => {
    set({ isLoading: true, error: null });
    try {
      const suiteData = await TestService.getTestSuite(repoName, suiteName);
      set({ currentSuite: suiteData, isLoading: false });
    } catch (error) {
      const storeError = handleStoreError(error, 'fetchTestSuite');
      set({ error: storeError.message, isLoading: false });
    }
  },

  saveTestSuite: async (repoName: string, suiteData: TestSuiteData) => {
    set({ isLoading: true, error: null });
    try {
      const savedSuite = await TestService.saveTestSuite(repoName, suiteData);
      set({ currentSuite: savedSuite, isLoading: false });
      
      // Refresh test suites list
      await get().fetchTestSuites(repoName);
    } catch (error) {
      const storeError = handleStoreError(error, 'saveTestSuite');
      set({ error: storeError.message, isLoading: false });
    }
  },

  deleteTestSuite: async (repoName: string, suiteName: string) => {
    set({ isLoading: true, error: null });
    try {
      await TestService.deleteTestSuite(repoName, suiteName);
      set({ currentSuite: null, isLoading: false });
      
      // Refresh test suites list
      await get().fetchTestSuites(repoName);
    } catch (error) {
      const storeError = handleStoreError(error, 'deleteTestSuite');
      set({ error: storeError.message, isLoading: false });
    }
  },

  // Execution actions
  executeTestSuite: async (repoName: string, suiteName: string, testNames?: string[]) => {
    set({ isLoading: true, error: null });
    try {
      const executionResult = await TestService.executeTestSuite(repoName, suiteName, testNames);
      set({ currentExecution: executionResult, isLoading: false });
      
      // Refresh execution history
      await get().fetchExecutionHistory(repoName, suiteName);
    } catch (error) {
      const storeError = handleStoreError(error, 'executeTestSuite');
      set({ error: storeError.message, isLoading: false });
    }
  },

  executeSingleTest: async (repoName: string, suiteName: string, testName: string) => {
    set({ isLoading: true, error: null });
    try {
      const testResult = await TestService.executeSingleTest(repoName, suiteName, testName);
      
      // Create a suite execution result with single test
      const suiteExecution: TestSuiteExecutionResult = {
        suite_name: suiteName,
        test_results: [testResult],
        total_tests: 1,
        passed_tests: testResult.overall_passed ? 1 : 0,
        failed_tests: testResult.overall_passed ? 0 : 1,
        total_execution_time_ms: testResult.execution_time_ms,
        executed_at: testResult.executed_at,
      };
      
      set({ currentExecution: suiteExecution, isLoading: false });
    } catch (error) {
      const storeError = handleStoreError(error, 'executeSingleTest');
      set({ error: storeError.message, isLoading: false });
    }
  },

  fetchExecutionHistory: async (repoName: string, suiteName: string, limit: number = 10) => {
    set({ isLoading: true, error: null });
    try {
      const history = await TestService.getExecutionHistory(repoName, suiteName, limit);
      set({ executionHistory: history, isLoading: false });
    } catch (error) {
      const storeError = handleStoreError(error, 'fetchExecutionHistory');
      set({ error: storeError.message, isLoading: false });
    }
  },

  fetchLatestExecution: async (repoName: string, suiteName: string) => {
    set({ isLoading: true, error: null });
    try {
      const latestExecution = await TestService.getLatestExecution(repoName, suiteName);
      set({ currentExecution: latestExecution, isLoading: false });
    } catch (error) {
      const storeError = handleStoreError(error, 'fetchLatestExecution');
      set({ error: storeError.message, isLoading: false });
    }
  },

  // Local state mutations
  setCurrentSuite: (suite: TestSuiteData | null) => {
    set({ currentSuite: suite });
  },

  setCurrentExecution: (execution: TestSuiteExecutionResult | null) => {
    set({ currentExecution: execution });
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

  clearTestData: () => {
    set({
      testSuites: [],
      currentSuite: null,
      currentExecution: null,
      executionHistory: [],
      error: null,
    });
  },
});