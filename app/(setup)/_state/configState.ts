import { useState, useRef, useEffect, useCallback } from "react";
import { postConfigDataDebounced } from '../_lib/postConfigData';

export interface SetupData {
  hostingType: "self" | "multi-user" | "";
  githubClientId: string;
  githubClientSecret: string;
  llmConfigs: Array<{
    provider: string;
    model: string;
    apiKey: string;
  }>;
  currentStep: {
    step: number;
    selectedProvider: string;
    selectedModel: string;
    apiKey: string;
  };
}

const defaultSetupData: SetupData = {
  hostingType: "",
  githubClientId: "",
  githubClientSecret: "",
  llmConfigs: [],
  currentStep: {
    step: 1,
    selectedProvider: "",
    selectedModel: "",
    apiKey: "",
  },
};

// Immediate persistence helper
const persistState = (state: SetupData) => {
  if (typeof window !== "undefined") {
    window.localStorage.setItem("interviewSetupData", JSON.stringify(state));
  }
};

export function useConfigState() {
  const [configState, setConfigState] = useState<SetupData>(defaultSetupData);
  const hasRestoredSetupData = useRef(false);

  useEffect(() => {
    if (!hasRestoredSetupData.current && typeof window !== "undefined") {
      const saved = window.localStorage.getItem("interviewSetupData");
      if (saved) {
        try {
          const parsed = JSON.parse(saved);
          const valid =
            typeof parsed === "object" &&
            parsed !== null &&
            typeof parsed.currentStep === "object" &&
            typeof parsed.currentStep.step === "number" &&
            parsed.currentStep.step >= 1 &&
            typeof parsed.hostingType === "string" &&
            typeof parsed.githubClientId === "string" &&
            typeof parsed.githubClientSecret === "string" &&
            Array.isArray(parsed.llmConfigs);
          
          if (valid) {
            // Clear temporary LLM fields on page load/refresh
            const restoredState = {
              ...parsed,
              currentStep: {
                ...parsed.currentStep,
                selectedProvider: "",
                selectedModel: "",
                apiKey: "",
              }
            };
            setConfigState(restoredState);
          } else {
            setConfigState(defaultSetupData);
          }
        } catch {
          setConfigState(defaultSetupData);
        }
      }
      hasRestoredSetupData.current = true;
    }
  }, []);

  // Enhanced setter that immediately persists
  const updateConfigState = useCallback((updater: SetupData | ((prev: SetupData) => SetupData)) => {
    setConfigState(prev => {
      const newState = typeof updater === 'function' ? updater(prev) : updater;
      persistState(newState);
      return newState;
    });
  }, []);

  // Individual field updaters with immediate persistence
  const updateHostingType = useCallback((type: "self" | "multi-user" | "") => {
    updateConfigState(prev => ({ ...prev, hostingType: type }));
  }, [updateConfigState]);

  const updateGithubClientId = useCallback((id: string) => {
    updateConfigState(prev => ({ ...prev, githubClientId: id }));
  }, [updateConfigState]);

  const updateGithubClientSecret = useCallback((secret: string) => {
    updateConfigState(prev => ({ ...prev, githubClientSecret: secret }));
  }, [updateConfigState]);

  const updateCurrentStepField = useCallback((field: keyof SetupData['currentStep'], value: string | number | boolean) => {
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
        llmConfigs: [...prev.llmConfigs, newConfig],
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
      llmConfigs: prev.llmConfigs.filter((_, i) => i !== index)
    }));
  }, [updateConfigState]);

  return {
    configState,
    setConfigState: updateConfigState,
    updateHostingType,
    updateGithubClientId,
    updateGithubClientSecret,
    updateCurrentStepField,
    addLLMConfig,
    removeLLMConfig,
  };
}