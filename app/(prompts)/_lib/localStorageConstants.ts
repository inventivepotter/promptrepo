/**
 * Local storage key constants
 */

export const LOCAL_STORAGE_KEYS = {
  /** Key for storing prompts data */
  PROMPTS_DATA: 'promptsData',
  
  /** Key for storing configured repositories */
  CONFIGURED_REPOS: 'configuredRepos',

  /** Key for storing configured models */
  CONFIGURED_MODELS: 'configuredModels'
} as const;

export type LocalStorageKey = typeof LOCAL_STORAGE_KEYS[keyof typeof LOCAL_STORAGE_KEYS];