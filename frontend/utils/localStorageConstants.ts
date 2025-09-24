/**
 * Local storage key constants
 */

export const LOCAL_STORAGE_KEYS = {
  /** Key for storing prompts data */
  PROMPTS_DATA: 'promptsData',
  
  /** Key for storing configured repositories */
  CONFIGURED_REPOS: 'configuredRepos',

  /** Key for storing configured models */
  CONFIGURED_MODELS: 'configuredModels',
  
  /** Key for storing pricing data */
  PRICING_DATA: 'pricingData',
  
  /** Key for storing auth session */
  AUTH_SESSION: 'auth_session',
  
  /** Key for storing user data (in sessionStorage) */
  USER_DATA: 'user_data',
  
  /** Key for storing refresh token */
  REFRESH_TOKEN: 'refresh_token'
} as const;

export type LocalStorageKey = typeof LOCAL_STORAGE_KEYS[keyof typeof LOCAL_STORAGE_KEYS];