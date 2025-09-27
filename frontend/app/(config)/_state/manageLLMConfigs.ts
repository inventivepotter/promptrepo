import { useCallback } from 'react';
import { ConfigState } from '../_types/state';
import { LLMProviderService } from '@/services/llm/llmProvider/llmProviderService';
import { errorNotification } from '@/lib/notifications';
import type { components } from '@/types/generated/api';

type LLMConfig = components['schemas']['LLMConfig'];

export function useLLMConfigActions(
  configState: ConfigState,
  setConfigState: React.Dispatch<React.SetStateAction<ConfigState>>
) {
  // Load available providers
  const loadAvailableLLMProviders = useCallback(async () => {
    setConfigState(prev => ({
      ...prev,
      providers: { ...prev.providers, isLoading: true }
    }));

    try {
      const providersData = await LLMProviderService.getAvailableProviders();
      setConfigState(prev => ({
        ...prev,
        providers: {
          ...prev.providers,
          available: providersData.providers,
          isLoading: false,
        }
      }));
    } catch (error) {
      setConfigState(prev => ({
        ...prev,
        providers: { ...prev.providers, isLoading: false }
      }));
    }
  }, [setConfigState]);

  // Add LLM config
  const addLLMConfig = useCallback(() => {
    const { selectedProvider, selectedModel, apiKey, apiBaseUrl } = configState.currentStep;
    
    if (!selectedProvider || !selectedModel || !apiKey) return;

    const newConfig: LLMConfig = {
      id: "",
      provider: selectedProvider,
      model: selectedModel,
      api_key: apiKey,
      api_base_url: apiBaseUrl,
      scope: 'user'
    };

    // Check for duplicates
    const isDuplicate = configState.config.llm_configs?.some(existing =>
      existing.provider === newConfig.provider &&
      existing.model === newConfig.model &&
      existing.api_key === newConfig.api_key &&
      existing.api_base_url === newConfig.api_base_url
    );

    if (isDuplicate) {
      errorNotification(
        'Duplicate Configuration',
        'This LLM configuration already exists.'
      );
      return;
    }

    setConfigState(prev => ({
      ...prev,
      config: {
        ...prev.config,
        llm_configs: [...(prev.config.llm_configs || []), newConfig],
      },
      currentStep: {
        ...prev.currentStep,
        selectedProvider: "",
        selectedModel: "",
        apiKey: "",
        apiBaseUrl: ""
      }
    }));
  }, [configState.currentStep, configState.config.llm_configs, setConfigState]);

  // Remove LLM config
  const removeLLMConfig = useCallback((index: number) => {
    setConfigState(prev => ({
      ...prev,
      config: {
        ...prev.config,
        llm_configs: prev.config.llm_configs?.filter((_, i) => i !== index) || []
      }
    }));
  }, [setConfigState]);

  return {
    loadAvailableLLMProviders,
    addLLMConfig,
    removeLLMConfig,
  };
}