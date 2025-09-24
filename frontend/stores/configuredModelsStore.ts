import { localStorage } from "@/lib/localStorage";
import type { components } from '@/types/generated/api';
import { LOCAL_STORAGE_KEYS } from '@/utils/localStorageConstants';

type ProviderInfo = components['schemas']['ProviderInfo'];

// ==========================================
// Storage Operations
// ==========================================

/**
 * Gets all configured models from localStorage
 * @returns Array of configured provider info or empty array
 */
export const getConfiguredModels = (): ProviderInfo[] => {
  if (typeof window === 'undefined') {
    return [];
  }

  try {
    const saved = localStorage.get<ProviderInfo[]>(LOCAL_STORAGE_KEYS.CONFIGURED_MODELS);
    if (!saved || !Array.isArray(saved)) {
      return [];
    }
    
    // Validate the data structure
    const isValidProviderArray = saved.every((item: unknown) =>
      item && typeof item === 'object' &&
      'id' in item && typeof item.id === 'string' &&
      'name' in item && typeof item.name === 'string' &&
      'models' in item && Array.isArray(item.models)
    );
    
    return isValidProviderArray ? saved as ProviderInfo[] : [];
  } catch (error) {
    console.error('Error getting configured models from storage:', error);
    return [];
  }
};

/**
 * Clears all configured models from localStorage
 */
export const clearConfiguredModels = (): void => {
  if (typeof window === 'undefined') {
    return;
  }

  try {
    localStorage.clear(LOCAL_STORAGE_KEYS.CONFIGURED_MODELS);
  } catch (error) {
    console.error('Error clearing configured models from storage:', error);
  }
};

/**
 * Sets all configured models in localStorage
 * @param models - Array of configured provider info to store
 */
export const setConfiguredModels = (models: ProviderInfo[]): void => {
  if (typeof window === 'undefined') {
    return;
  }

  try {
    localStorage.set(LOCAL_STORAGE_KEYS.CONFIGURED_MODELS, models);
  } catch (error) {
    console.error('Error setting configured models in storage:', error);
  }
};

// ==========================================
// Model Operations
// ==========================================

/**
 * Adds a new configured model to localStorage
 * @param newProvider - New provider info to add
 */
export const addConfiguredModel = (newProvider: ProviderInfo): void => {
  if (typeof window === 'undefined') {
    return;
  }

  try {
    const currentModels = getConfiguredModels();
    const updatedModels = [...currentModels, newProvider];
    setConfiguredModels(updatedModels);
  } catch (error) {
    console.error('Error adding configured model to storage:', error);
  }
};

/**
 * Updates a configured model in localStorage
 * @param providerId - ID of the provider to update
 * @param updatedProvider - Updated provider info
 */
export const updateConfiguredModel = (providerId: string, updatedProvider: ProviderInfo): void => {
  if (typeof window === 'undefined') {
    return;
  }

  try {
    const currentModels = getConfiguredModels();
    const updatedModels = currentModels.map(provider =>
      provider.id === providerId ? updatedProvider : provider
    );
    setConfiguredModels(updatedModels);
  } catch (error) {
    console.error('Error updating configured model in storage:', error);
  }
};

/**
 * Removes a configured model from localStorage
 * @param providerId - ID of the provider to remove
 */
export const removeConfiguredModel = (providerId: string): void => {
  if (typeof window === 'undefined') {
    return;
  }

  try {
    const currentModels = getConfiguredModels();
    const updatedModels = currentModels.filter(provider => provider.id !== providerId);
    setConfiguredModels(updatedModels);
  } catch (error) {
    console.error('Error removing configured model from storage:', error);
  }
};

// ==========================================
// Provider Operations
// ==========================================

/**
 * Checks if a provider is configured in localStorage
 * @param providerId - ID of the provider to check
 * @returns True if the provider is configured, false otherwise
 */
export const hasProvider = (providerId: string): boolean => {
  if (typeof window === 'undefined') {
    return false;
  }

  try {
    const currentModels = getConfiguredModels();
    return currentModels.some(provider => provider.id === providerId);
  } catch (error) {
    console.error('Error checking provider in storage:', error);
    return false;
  }
};

/**
 * Gets a configured provider from localStorage
 * @param providerId - ID of the provider to get
 * @returns ProviderInfo if found, null otherwise
 */
export const getConfiguredProvider = (providerId: string): ProviderInfo | null => {
  if (typeof window === 'undefined') {
    return null;
  }

  try {
    const currentModels = getConfiguredModels();
    return currentModels.find(provider => provider.id === providerId) || null;
  } catch (error) {
    console.error('Error getting configured provider from storage:', error);
    return null;
  }
};

// ==========================================
// Backward Compatibility Exports
// ==========================================

// Maintain backward compatibility with old function names
export const getConfiguredModelsFromStorage = getConfiguredModels;
export const clearConfiguredModelsFromStorage = clearConfiguredModels;
export const storeConfiguredModels = setConfiguredModels;
export const addConfiguredModelToStorage = addConfiguredModel;
export const updateConfiguredModelInStorage = updateConfiguredModel;
export const removeConfiguredModelFromStorage = removeConfiguredModel;
export const isProviderConfiguredInStorage = hasProvider;
export const getConfiguredProviderFromStorage = getConfiguredProvider;