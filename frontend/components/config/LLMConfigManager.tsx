"use client"

import {
  VStack,
  Box,
  Text,
  Button,
  Input,
  Combobox,
  createListCollection,
  HStack
} from '@chakra-ui/react'
import React, { useState, useEffect } from "react";
import { FaChevronDown } from 'react-icons/fa';
import type { components } from '@/types/generated/api';
import { useConfig, useConfigActions, useAvailableProviders, useLLMFormState } from '@/stores/configStore';
import { useLoadingStore } from '@/stores/loadingStore';

type LLMConfig = components['schemas']['LLMConfig'];
type BasicProviderInfo = components['schemas']['BasicProviderInfo'];
type ModelInfo = components['schemas']['ModelInfo'];

interface LLMConfigManagerProps {
  disabled?: boolean
}

export default function LLMConfigManager({
  disabled = false
}: LLMConfigManagerProps) {
  const config = useConfig();
  const {
    addLLMConfig,
    removeLLMConfig,
    loadAvailableLLMProviders,
    getModels,
    setLLMProvider,
    setApiKey,
    setLLMModel,
    setApiBaseUrl,
    resetLLMForm,
    updateConfig
  } = useConfigActions();
  const availableProviders = useAvailableProviders();
  const { llmProvider, apiKey, llmModel, apiBaseUrl, availableModels, isLoadingModels } = useLLMFormState();
  const { isLoading, showLoading, hideLoading } = useLoadingStore();
  
  // Local state only for UI-specific concerns
  const [isLoadingProviders, setIsLoadingProviders] = useState(false);
  const [isFetchingModels, setIsFetchingModels] = useState(false);
  
  // Load providers on mount using global loading
  useEffect(() => {
    const loadData = async () => {
      setIsLoadingProviders(true);
      showLoading('Loading Providers', 'Fetching available LLM providers...');
      try {
        await loadAvailableLLMProviders();
      } finally {
        setIsLoadingProviders(false);
        hideLoading();
      }
    };
    if (availableProviders.length === 0) {
      loadData();
    }
  }, [loadAvailableLLMProviders, availableProviders.length, showLoading, hideLoading]);
  
  const llmConfigs = config.llm_configs || [];
  const [providerSearchValue, setProviderSearchValue] = useState('');
  const [modelSearchValue, setModelSearchValue] = useState('');

  // Find the current provider to check if it requires custom API base
  const currentProvider = availableProviders.find(p => p.id === llmProvider);
  const requiresApiBase = currentProvider?.custom_api_base || false;

  // Filter providers based on search value
  const filteredProviders = (Array.isArray(availableProviders) ? availableProviders : [])
    .filter(provider =>
      provider.name.toLowerCase().includes(providerSearchValue.toLowerCase()) ||
      provider.id.toLowerCase().includes(providerSearchValue.toLowerCase())
    );

  // Filter models based on search value
  const filteredModels = (Array.isArray(availableModels) ? availableModels : [])
    .filter(model =>
      model.name.toLowerCase().includes(modelSearchValue.toLowerCase()) ||
      model.id.toLowerCase().includes(modelSearchValue.toLowerCase())
    );

  // Fetch models when provider and API key are available
  useEffect(() => {
    const fetchModels = async () => {
      if (!llmProvider || !apiKey || apiKey.length < 3) {
        return;
      }

      // For providers that require API base, wait until it's provided
      if (requiresApiBase && (!apiBaseUrl || apiBaseUrl.length < 3)) {
        return;
      }

      setIsFetchingModels(true);
      try {
        await getModels();
      } finally {
        setIsFetchingModels(false);
      }
    };

    // Debounce the API call
    const timeoutId = setTimeout(fetchModels, 500);
    return () => clearTimeout(timeoutId);
  }, [llmProvider, apiKey, apiBaseUrl, requiresApiBase, getModels]);

  // Clear selected model when provider changes
  const handleProviderChange = (newProvider: string) => {
    setLLMProvider(newProvider);
    if (newProvider !== llmProvider) {
      setLLMModel('');
    }
  };

  const handleAddConfiguration = async () => {
    showLoading('Adding Configuration', 'Saving your LLM configuration...');
    
    const newConfig: LLMConfig = {
      id: '',
      provider: llmProvider,
      model: llmModel,
      api_key: apiKey,
      api_base_url: requiresApiBase ? apiBaseUrl : '',
      scope: 'user'
    };
    
    addLLMConfig(newConfig);
    
    // Update config to persist to backend
    const updatedConfig = {
      ...config,
      llm_configs: [...(config.llm_configs || []), newConfig]
    };
    
    try {
      await updateConfig(updatedConfig);
      
      // Reset form
      resetLLMForm();
      setProviderSearchValue('');
      setModelSearchValue('');
    } catch (error) {
      console.error('Error saving configuration:', error);
    } finally {
      hideLoading();
    }
  };

  const handleRemoveConfig = async (index: number) => {
    showLoading('Removing Configuration', 'Removing LLM configuration...');
    
    const providerToRemove = llmConfigs[index]?.provider;
    removeLLMConfig(index);
    
    // Update config to persist to backend
    const updatedConfig = {
      ...config,
      llm_configs: config.llm_configs?.filter(c => c.provider !== providerToRemove) || []
    };
    
    try {
      await updateConfig(updatedConfig);
    } catch (error) {
      console.error('Error removing configuration:', error);
    } finally {
      hideLoading();
    }
  };

  return (
    <Box p={6} borderWidth="1px" borderRadius="md" borderColor="border.emphasized">
      <VStack gap={6} align="stretch">
        <Text fontSize="lg" fontWeight="bold">LLM Provider Configuration</Text>
        <Text fontSize="sm" opacity={0.7} mb={2}>
          Setup your AI provider and API key first, then select from available models.
        </Text>
        {/* Add new LLM configuration */}
        <Box p={6} borderWidth="1px" borderRadius="md" borderColor="border.muted">
          <VStack gap={4}>
            {/* Step 1: Provider and API Key on same line */}
            <Box width="100%">
              <Text mb={2} fontWeight="medium">1. LLM Provider & API Key</Text>
              <HStack gap={4}>
                <Box flex={1}>
                  <Combobox.Root
                    collection={createListCollection({
                      items: filteredProviders.map((p: BasicProviderInfo) => ({ label: p.name, value: p.id }))
                    })}
                    value={[llmProvider]}
                    onValueChange={(e) => {
                      const newProvider = e.value?.[0] || '';
                      handleProviderChange(newProvider);
                    }}
                    inputValue={providerSearchValue}
                    onInputValueChange={(e) => setProviderSearchValue(e.inputValue)}
                    openOnClick
                    disabled={disabled || isLoadingProviders}
                  >
                    <Combobox.Control position="relative">
                      <Combobox.Input
                        placeholder={isLoadingProviders ? "Loading providers..." : "Select provider"}
                        paddingRight="2rem"
                        disabled={disabled || isLoadingProviders}
                      />
                      <Combobox.Trigger position="absolute" right="0.5rem" top="50%" transform="translateY(-50%)">
                        <FaChevronDown size={16} />
                      </Combobox.Trigger>
                    </Combobox.Control>
                    <Combobox.Positioner>
                      <Combobox.Content>
                        {filteredProviders.map((provider: BasicProviderInfo) => (
                          <Combobox.Item key={provider.id} item={provider.id}>
                            <Combobox.ItemText>{provider.name}</Combobox.ItemText>
                            <Combobox.ItemIndicator />
                          </Combobox.Item>
                        ))}
                      </Combobox.Content>
                    </Combobox.Positioner>
                  </Combobox.Root>
                </Box>
                <Box flex={1}>
                  <Input
                    type="password"
                    placeholder="Enter your API key"
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                    disabled={disabled || !llmProvider}
                  />
                </Box>
              </HStack>
              <Text fontSize="sm" opacity={0.7} mt={2}>
                Both provider and API key are required to fetch available models.
              </Text>
            </Box>

            {/* Step 1.5: API Base URL (conditional) */}
            {llmProvider && requiresApiBase && (
              <Box width="100%">
                <Text mb={2} fontWeight="medium">API Base URL</Text>
                <Input
                  placeholder="Enter API base URL (e.g., http://localhost:1234/v1, http://host.docker.internal:1234/v1)"
                  value={apiBaseUrl}
                  onChange={(e) => setApiBaseUrl(e.target.value)}
                  disabled={disabled}
                />
                <Text fontSize="sm" opacity={0.7} mt={1}>
                  Custom API endpoint for {currentProvider?.name}
                </Text>
              </Box>
            )}

            {/* Step 2: Select Model (after provider, API key, and API base URL if required are entered) */}
            {llmProvider && apiKey && apiKey.length >= 3 && (!requiresApiBase || (apiBaseUrl && apiBaseUrl.length >= 3)) && (
              <Box width="100%">
                <Text mb={2} fontWeight="medium">2. Model</Text>
                <Combobox.Root
                  collection={createListCollection({
                    items: filteredModels.map((m: ModelInfo) => ({ label: m.name, value: m.id }))
                  })}
                  value={[llmModel]}
                  onValueChange={(e) => setLLMModel(e.value[0] || '')}
                  inputValue={modelSearchValue}
                  onInputValueChange={(e) => setModelSearchValue(e.inputValue)}
                  openOnClick
                  disabled={disabled || isFetchingModels || isLoadingModels}
                >
                  <Combobox.Control position="relative">
                    <Combobox.Input
                      placeholder={isFetchingModels || isLoadingModels ? "Fetching models..." : "Select model"}
                      paddingRight="2rem"
                      disabled={disabled || isFetchingModels || isLoadingModels}
                    />
                    <Combobox.Trigger position="absolute" right="0.5rem" top="50%" transform="translateY(-50%)">
                      <FaChevronDown size={16} />
                    </Combobox.Trigger>
                  </Combobox.Control>
                  <Combobox.Positioner>
                    <Combobox.Content>
                      {filteredModels.map((model: ModelInfo) => (
                        <Combobox.Item key={model.id} item={model.id}>
                          <Combobox.ItemText>{model.name}</Combobox.ItemText>
                          <Combobox.ItemIndicator />
                        </Combobox.Item>
                      ))}
                    </Combobox.Content>
                  </Combobox.Positioner>
                </Combobox.Root>
                {(isFetchingModels || isLoadingModels) && (
                  <Text fontSize="sm" opacity={0.7} mt={1}>
                    Fetching available models for {(Array.isArray(availableProviders) ? availableProviders : []).find((p: BasicProviderInfo) => p.id === llmProvider)?.name}...
                  </Text>
                )}
                {!isFetchingModels && !isLoadingModels && availableModels.length === 0 && apiKey && apiKey.length >= 3 && (!requiresApiBase || (apiBaseUrl && apiBaseUrl.length >= 3)) && (
                  <Text fontSize="sm" color="red.500" mt={1}>
                    Unable to fetch models. Please check your API key{requiresApiBase ? ' and API base URL' : ''}.
                  </Text>
                )}
              </Box>
            )}
            
            <Button
              onClick={handleAddConfiguration}
              disabled={
                !llmProvider ||
                !llmModel ||
                !apiKey ||
                (requiresApiBase && !apiBaseUrl) ||
                disabled
              }
              mt={4}
            >
              Add Configuration
            </Button>
          </VStack>
        </Box>
        {/* Display configured LLMs */}
        {llmConfigs.length > 0 && (
          <Box p={6} borderWidth="1px" borderRadius="md" borderColor="border.muted">
            <Text fontWeight="bold" mb={4}>Configured LLM Providers</Text>
            <VStack gap={2}>
              {llmConfigs.map((config, index) => {
                const isOrgScope = config.scope === 'organization';
                return (
                  <HStack key={index} justify="space-between" width="100%" p={2} bg="bg.subtle" borderRadius="md">
                    <Text fontSize="sm" fontWeight="400">
                      Provider: <Text as="span" fontWeight="bold">{config.provider}</Text> | Model: <Text as="span" fontWeight="bold">{config.model}</Text>
                      {!isOrgScope && config.api_base_url && (
                        <> | API Base: <Text as="span" fontWeight="bold">{config.api_base_url}</Text></>
                      )}
                      {isOrgScope && (
                        <Text as="span" fontSize="xs" color="gray.500" ml={2}>(Organization Scoped)</Text>
                      )}
                    </Text>
                    <Button
                      size="sm"
                      onClick={() => handleRemoveConfig(index)}
                      disabled={disabled || isOrgScope}
                    >
                      Remove
                    </Button>
                  </HStack>
                );
              })}
            </VStack>
          </Box>
        )}
      </VStack>
    </Box>
  )
}