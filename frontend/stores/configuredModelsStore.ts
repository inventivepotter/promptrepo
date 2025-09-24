import { localStorage } from "@/lib/localStorage";
import type { components } from '@/types/generated/api';

type ProviderInfo = components['schemas']['ProviderInfo'];
const STORE_NAME = 'configuredRepos';

/**
 * Store configured models to localStorage
 * @param configuredModels - Array of configured provider info to store
 */
export const storeConfiguredModels = (configuredModels: ProviderInfo[]): void => {
  localStorage.set(STORE_NAME, configuredModels);
};

/**
 * Get configured models from localStorage
 * @returns Array of configured provider info from storage
 */
export const getConfiguredModelsFromStorage = (): ProviderInfo[] => {
  const saved = localStorage.get<ProviderInfo[]>(STORE_NAME);
  if (saved && Array.isArray(saved)) {
    // Validate the data structure
    const isValidProviderArray = saved.every((item: unknown) =>
      item && typeof item === 'object' &&
      'id' in item && typeof item.id === 'string' &&
      'name' in item && typeof item.name === 'string' &&
      'models' in item && Array.isArray(item.models)
    );
    
    if (isValidProviderArray) {
      return saved as ProviderInfo[];
    }
  }
  return [];
};

/**
 * Clear configured models from localStorage
 */
export const clearConfiguredModelsFromStorage = (): void => {
  localStorage.clear(STORE_NAME);
};

/**
 * Update a specific configured model in storage
 * @param providerId - ID of the provider to update
 * @param updatedProvider - Updated provider info
 */
export const updateConfiguredModelInStorage = (providerId: string, updatedProvider: ProviderInfo): void => {
  const currentModels = getConfiguredModelsFromStorage();
  const updatedModels = currentModels.map(provider =>
    provider.id === providerId ? updatedProvider : provider
  );
  storeConfiguredModels(updatedModels);
};

/**
 * Add a new configured model to storage
 * @param newProvider - New provider info to add
 */
export const addConfiguredModelToStorage = (newProvider: ProviderInfo): void => {
  const currentModels = getConfiguredModelsFromStorage();
  const updatedModels = [...currentModels, newProvider];
  storeConfiguredModels(updatedModels);
};

/**
 * Remove a configured model from storage
 * @param providerId - ID of the provider to remove
 */
export const removeConfiguredModelFromStorage = (providerId: string): void => {
  const currentModels = getConfiguredModelsFromStorage();
  const updatedModels = currentModels.filter(provider => provider.id !== providerId);
  storeConfiguredModels(updatedModels);
};

/**
 * Check if a specific provider is configured in storage
 * @param providerId - ID of the provider to check
 * @returns boolean indicating if provider exists
 */
export const isProviderConfiguredInStorage = (providerId: string): boolean => {
  const currentModels = getConfiguredModelsFromStorage();
  return currentModels.some(provider => provider.id === providerId);
};

/**
 * Get a specific configured provider from storage
 * @param providerId - ID of the provider to get
 * @returns ProviderInfo if found, null otherwise
 */
export const getConfiguredProviderFromStorage = (providerId: string): ProviderInfo | null => {
  const currentModels = getConfiguredModelsFromStorage();
  return currentModels.find(provider => provider.id === providerId) || null;
};