import { useState, useRef, useEffect, useCallback } from "react";
import { ConfigState } from '../_types/state';
import { fetchConfigFromBackend } from '../_lib/getConfigData';

const defaultSetupData: ConfigState = {
  config: {
    hostingType: "",
    githubClientId: "",
    githubClientSecret: "",
    llmConfigs: [],
  },
  currentStep: {
    step: 1,
    selectedProvider: "",
    selectedModel: "",
    apiKey: "",
  },
  isLoading: false,
};

export function useConfigState() {
  const [configState, setConfigState] = useState<ConfigState>(defaultSetupData);
  const hasRestoredSetupData = useRef(false);

  useEffect(() => {
      const loadConfigFromBackend = async () => {
        try {
          const config = await fetchConfigFromBackend();
          const cleanedState: ConfigState = {
            config,
            currentStep: {
              step: 1,
              selectedProvider: "",
              selectedModel: "",
              apiKey: "",
            },
            isLoading: false,
          };

          setConfigState(cleanedState);
        } catch (error) {
          setConfigState(defaultSetupData);
        } finally {
          hasRestoredSetupData.current = true;
        }
      };
      loadConfigFromBackend();
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