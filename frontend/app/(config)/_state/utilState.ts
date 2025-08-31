import { useState, useRef, useCallback } from "react";
import { LLMConfig } from '@/types/Configuration';
import { LLMProvider } from "@/types/LLMProvider";
import { modelsApi } from '../_lib/api/modelsApi';
import { errorNotification } from '@/lib/notifications';

interface UtilState {
  githubClientId: string;
  githubClientSecret: string;
  selectedProvider: string;
  selectedModel: string;
  apiKey: string;
  apiBaseUrl: string;
  llmConfigs: LLMConfig[];
  providers: {
    available: LLMProvider[];
    isLoading: boolean;
    error: string | null;
  };
}

const initUtilState: UtilState = {
  githubClientId: '',
  githubClientSecret: '',
  selectedProvider: '',
  selectedModel: '',
  apiKey: '',
  apiBaseUrl: '',
  llmConfigs: [],
  providers: {
    available: [],
    isLoading: false,
    error: null,
  }
};

export function useUtilState() {
  const [utilState, setUtilState] = useState<UtilState>(initUtilState);
  const providersLoadingRef = useRef(false);
  const providersLoadedRef = useRef(false);

  // Load providers
  const loadProviders = useCallback(async () => {
    // Skip if already loaded or currently loading
    if (providersLoadedRef.current || providersLoadingRef.current) {
      return;
    }

    providersLoadingRef.current = true;
    setUtilState(prev => ({
      ...prev,
      providers: {
        ...prev.providers,
        isLoading: true,
        error: null,
      }
    }));

    try {
      const result = await modelsApi.getAvailableProviders();
      if (result.success && result.data && result.data.providers) {
        setUtilState(prev => ({
          ...prev,
          providers: {
            available: result.data.providers,
            isLoading: false,
            error: null,
          }
        }));
        providersLoadedRef.current = true;
      } else {
        const errorMsg = 'error' in result ? result.error : 'Unknown error';
        setUtilState(prev => ({
          ...prev,
          providers: {
            available: [],
            isLoading: false,
            error: errorMsg,
          }
        }));
      }
    } catch (error) {
      setUtilState(prev => ({
        ...prev,
        providers: {
          available: [],
          isLoading: false,
          error: 'Failed to load providers',
        }
      }));
    } finally {
      providersLoadingRef.current = false;
    }
  }, []);

  // Update field helper
  const updateField = useCallback((field: keyof UtilState, value: unknown) => {
    setUtilState(prev => ({
      ...prev,
      [field]: value
    }));
  }, []);

  // Add LLM config
  const addLLMConfig = useCallback(() => {
    if (utilState.selectedProvider && utilState.selectedModel && utilState.apiKey) {
      const newConfig: LLMConfig = {
        provider: utilState.selectedProvider,
        model: utilState.selectedModel,
        apiKey: utilState.apiKey,
        apiBaseUrl: utilState.apiBaseUrl || undefined
      };

      // Check for duplicates
      const isDuplicate = utilState.llmConfigs.some(existingConfig =>
        existingConfig.provider === newConfig.provider &&
        existingConfig.model === newConfig.model &&
        existingConfig.apiKey === newConfig.apiKey &&
        existingConfig.apiBaseUrl === newConfig.apiBaseUrl
      );

      if (isDuplicate) {
        errorNotification(
          'Duplicate Configuration',
          'This LLM configuration already exists. The combination of provider, model, API base URL, and API key must be unique.'
        );
        return;
      }

      setUtilState(prev => ({
        ...prev,
        llmConfigs: [...prev.llmConfigs, newConfig],
        selectedProvider: '',
        selectedModel: '',
        apiKey: '',
        apiBaseUrl: ''
      }));
    }
  }, [utilState.selectedProvider, utilState.selectedModel, utilState.apiKey, utilState.apiBaseUrl, utilState.llmConfigs]);

  // Remove LLM config
  const removeLLMConfig = useCallback((index: number) => {
    setUtilState(prev => ({
      ...prev,
      llmConfigs: prev.llmConfigs.filter((_, i) => i !== index)
    }));
  }, []);

  // Reset all
  const resetAll = useCallback(() => {
    setUtilState(initUtilState);
  }, []);

  return {
    utilState,
    updateField,
    addLLMConfig,
    removeLLMConfig,
    resetAll,
    loadProviders
  };
}