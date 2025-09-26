// Combined auth store actions
import { createLoginAction } from './login';
import { createLogoutAction } from './logout';
import { createLoginWithGithubAction } from './oauthCallbackGithub';
import { createRefreshSessionAction } from './refreshSession';
import { createInitializeAuthAction } from './initializeAuth';
import { createUpdateUserAction } from './updateUser';
import { createSetLoadingAction } from './setLoading';
import { createSetUserAction } from './setUser';
import { createSetErrorAction } from './setError';
import { createHandleAuthSuccessAction } from './handleAuthSuccess';
import type { StateCreator } from '@/lib/zustand';
import type { AuthStore, AuthActions } from '../types';

// Combine all actions into a single StateCreator
export const createAuthActions: StateCreator<AuthStore, [], [], AuthActions> = (set, get, api) => ({
  // Public actions
  ...createLoginAction(set, get, api),
  ...createLoginWithGithubAction(set, get, api),
  ...createLogoutAction(set, get, api),
  ...createRefreshSessionAction(set, get, api),
  ...createInitializeAuthAction(set, get, api),
  ...createUpdateUserAction(set, get, api),
  ...createHandleAuthSuccessAction(set, get, api),
  
  // Internal actions
  ...createSetLoadingAction(set, get, api),
  ...createSetUserAction(set, get, api),
  ...createSetErrorAction(set, get, api),
});