/**
 * Test Store - Main store file for DeepEval test management
 */
import { create } from 'zustand';
import { devtools, immer } from '@/lib/zustand';
import { initialTestState } from './state';
import { createTestActions } from './actions';
import type { TestStore } from './types';

/**
 * Create the test store with middleware
 * No persistence needed - test data should be fresh from server
 */
export const useTestStore = create<TestStore>()(
  devtools(
    immer((set, get, ...rest) => {
      return {
        ...initialTestState,
        ...createTestActions(set, get, ...rest),
      };
    }),
    {
      name: 'test-store',
      enabled: process.env.NODE_ENV === 'development',
    }
  )
);