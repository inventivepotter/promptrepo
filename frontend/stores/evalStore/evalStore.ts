/**
 * Eval Store - Main store file for DeepEval evaluation management
 */
import { create } from 'zustand';
import { devtools, immer } from '@/lib/zustand';
import { initialEvalState } from './state';
import { createEvalActions } from './actions';
import type { EvalStore } from './types';

/**
 * Create the eval store with middleware
 * No persistence needed - eval data should be fresh from server
 */
export const useEvalStore = create<EvalStore>()(
  devtools(
    immer((set, get, ...rest) => {
      return {
        ...initialEvalState,
        ...createEvalActions(set, get, ...rest),
      };
    }),
    {
      name: 'eval-store',
      enabled: process.env.NODE_ENV === 'development',
    }
  )
);