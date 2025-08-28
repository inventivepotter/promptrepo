import { useState, useRef, useEffect, useCallback } from "react";
import { ConfigState } from '../_types/state';
import { getConfig } from '../_lib/getConfig';
import { getAvailableModels } from '../_lib/getAvailableModels';

export const initConfig: ConfigState['config'] = {
  hostingType: "",
  githubClientId: "",
  githubClientSecret: "",
  llmConfigs: [],
};

export const initConfigState: ConfigState = {
  config: initConfig,
  currentStep: {
    step: 1,
    selectedProvider: "",
    selectedModel: "",
    apiKey: "",
  },
  isLoading: false,
  availableModels: [],
};

export function useConfigState() {
  const [configState, setConfigState] = useState<ConfigState>(initConfigState);
  const hasRestoredSetupData = useRef(false);
  // Global state to prevent duplicate API calls
  const globalLoadingRef = useRef(false);
  const globalDataLoadedRef = useRef(false);
  useEffect(() => {
      const loadConfigAndModels = async () => {
        // Skip if already loaded globally or currently loading
        if (globalDataLoadedRef.current || globalLoadingRef.current) {
          return;
        }

        globalLoadingRef.current = true;
        
        try {
          const config = await getConfig();
          const availableModels = await getAvailableModels();
          
          setConfigState({
            config,
            currentStep: {
              step: 1,
              selectedProvider: "",
              selectedModel: "",
              apiKey: "",
            },
            isLoading: false,
            availableModels,
          });
          
          // Mark as globally loaded
          globalDataLoadedRef.current = true;
        } catch (error) {
          globalLoadingRef.current = false;
          setConfigState(initConfigState);
        } finally {
          hasRestoredSetupData.current = true;
        }
      };
      
      loadConfigAndModels();
    }
  , []);

  const updateConfigState = useCallback((updater: ConfigState | ((prev: ConfigState) => ConfigState)) => {
    setConfigState(prev => {
      const newState = typeof updater === 'function' ? updater(prev) : updater;
      // Don't persist to backend - only persist when user clicks save
      return newState;
    });
  }, []);

  // Generic field updater for config fields
  const updateConfigField = useCallback(<K extends keyof ConfigState['config']>(
    field: K,
    value: ConfigState['config'][K]
  ) => {
    updateConfigState(prev => ({
      ...prev,
      config: { ...prev.config, [field]: value }
    }));
  }, [updateConfigState]);

  const updateCurrentStepField = useCallback((field: keyof ConfigState['currentStep'], value: string | number | boolean) => {
    updateConfigState(prev => ({
      ...prev,
      currentStep: { ...prev.currentStep, [field]: value }
    }));
  }, [updateConfigState]);

  const addLLMConfig = useCallback(() => {
    const currentStep = configState.currentStep;
    if (currentStep.selectedProvider && currentStep.selectedModel && currentStep.apiKey) {
      const newConfig = {
        provider: currentStep.selectedProvider,
        model: currentStep.selectedModel,
        apiKey: currentStep.apiKey
      };
      updateConfigState(prev => ({
        ...prev,
        config: {
          ...prev.config,
          llmConfigs: [...prev.config.llmConfigs, newConfig],
        },
        currentStep: {
          ...prev.currentStep,
          selectedProvider: "",
          selectedModel: "",
          apiKey: ""
        }
      }));
    }
  }, [configState.currentStep, updateConfigState]);

  const removeLLMConfig = useCallback((index: number) => {
    updateConfigState(prev => ({
      ...prev,
      config: {
        ...prev.config,
        llmConfigs: prev.config.llmConfigs.filter((_, i) => i !== index)
      }
    }));
  }, [updateConfigState]);

  const setIsLoading = useCallback((loading: boolean) => {
    updateConfigState(prev => ({
      ...prev,
      isLoading: loading
    }));
  }, [updateConfigState]);

  return {
    configState,
    setConfigState: updateConfigState,
    updateConfigField,
    updateCurrentStepField,
    addLLMConfig,
    removeLLMConfig,
    setIsLoading,
  };
}