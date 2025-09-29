"use client"

import {
  VStack,
  Box,
  Text,
  Button,
  Input,
  Combobox,
  createListCollection,
  HStack,
  Field,
} from '@chakra-ui/react'
import { FaChevronDown } from 'react-icons/fa';
import { useEffect } from 'react';
import type { components } from '@/types/generated/api';
import { useConfig, useConfigActions, useAvailableProviders, useLLMFormState, useLLMFormUIState, useConfigStore } from '@/stores/configStore';
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
    setApiKey,
    setLLMModel,
    setApiBaseUrl,
    resetLLMForm,
    updateConfig,
    setProviderSearchValue,
    setModelSearchValue,
    setLLMProviderWithSideEffects,
    fetchModelsIfReady,
  } = useConfigActions();
  const availableProviders = useAvailableProviders();
  const { llmProvider, apiKey, llmModel, apiBaseUrl, availableModels, isLoadingModels } = useLLMFormState();
  const { providerSearchValue, modelSearchValue } = useLLMFormUIState();
  const { isLoading, showLoading, hideLoading } = useLoadingStore();
  
  const llmConfigs = config.llm_configs || [];

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


  // Clear selected model when provider changes
  const handleProviderChange = async (newProvider: string) => {
    if (newProvider !== llmProvider) {
      setLLMModel('');
    }
    await setLLMProviderWithSideEffects(newProvider);
  };

  // Fetch models when API key or API base URL changes
  useEffect(() => {
    if (llmProvider && apiKey && apiKey.length >= 3 && (!requiresApiBase || (apiBaseUrl && apiBaseUrl.length >= 3))) {
      fetchModelsIfReady();
    }
  }, [apiKey, apiBaseUrl, llmProvider, requiresApiBase, fetchModelsIfReady]);

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
    
    // removeLLMConfig already updates the state correctly.
    // We just need to call updateConfig to persist the current state.
    removeLLMConfig(index);
    
    try {
      // Get the latest state directly from the store after the removal
      const currentState = useConfigStore.getState().config;
      await updateConfig(currentState);
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
          <VStack gap={4} width="100%">
            {/* Step 1: Provider and API Key on same line */}
            <Box width="100%">
              <HStack gap={4} width="100%" align="end">
                <Box flex={2}>
                  <Field.Root required>
                    <Field.Label>LLM Provider <Field.RequiredIndicator /></Field.Label>
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
                    disabled={disabled || isLoading}
                    width="100%"
                  >
                    <Combobox.Control position="relative">
                      <Combobox.Input
                        placeholder={isLoading ? "Loading providers..." : "Select provider"}
                        paddingRight="2rem"
                        disabled={disabled || isLoading}
                      />
                      <Combobox.IndicatorGroup position="absolute" right="0.5rem" top="50%" transform="translateY(-50%)">
                        <Combobox.Trigger>
                          <FaChevronDown size={16} />
                        </Combobox.Trigger>
                      </Combobox.IndicatorGroup>
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
                  </Field.Root>
                </Box>
                <Box flex={2}>
                  <Field.Root required>
                    <Field.Label>API Key <Field.RequiredIndicator /></Field.Label>
                    <Input
                    type="password"
                    placeholder="Enter your API key"
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                    disabled={disabled || !llmProvider}
                    width="100%"
                    />
                  </Field.Root>
                </Box>
                <Box display="flex" verticalAlign={"bottom"}>
                  <Button
                    onClick={handleAddConfiguration}
                    disabled={
                      !llmProvider ||
                      !llmModel ||
                      !apiKey ||
                      (requiresApiBase && !apiBaseUrl) ||
                      disabled
                    }
                    alignSelf="end"
                    verticalAlign={"bottom"}
                  >
                    Add Configuration
                  </Button>
                </Box>
              </HStack>
            </Box>

            {/* Step 1.5: API Base URL, Model, and other fields */}
            <Box width="100%">
              <HStack gap={4} width="100%" align="end">
                <Box flex={2.4}>
                  <Field.Root required={requiresApiBase}>
                    <Field.Label>API Base URL {requiresApiBase && <Field.RequiredIndicator />}</Field.Label>
                    <Input
                    placeholder="Enter API base URL (e.g., http://localhost:1234/v1)"
                    value={apiBaseUrl}
                    onChange={(e) => setApiBaseUrl(e.target.value)}
                    disabled={disabled || !llmProvider || !requiresApiBase}
                    width="100%"
                  />
                  {requiresApiBase && (
                    <Text fontSize="sm" opacity={0.7} mt={1}>
                      Custom API endpoint for {currentProvider?.name}
                    </Text>
                    )}
                  </Field.Root>
                </Box>
                <Box flex={2.4}>
                  <Field.Root required>
                    <Field.Label>Model <Field.RequiredIndicator /></Field.Label>
                    <Combobox.Root
                    collection={createListCollection({
                      items: filteredModels.map((m: ModelInfo) => ({ label: m.name, value: m.id }))
                    })}
                    value={[llmModel]}
                    onValueChange={(e) => setLLMModel(e.value[0] || '')}
                    inputValue={modelSearchValue}
                    onInputValueChange={(e) => setModelSearchValue(e.inputValue)}
                    openOnClick
                    disabled={disabled || !llmProvider || !apiKey || apiKey.length < 3 || (requiresApiBase && (!apiBaseUrl || apiBaseUrl.length < 3)) || isLoadingModels}
                    width="100%"
                  >
                    <Combobox.Control position="relative">
                      <Combobox.Input
                        placeholder={isLoadingModels ? "Fetching models..." : "Select model"}
                        paddingRight="2rem"
                        disabled={disabled || !llmProvider || !apiKey || apiKey.length < 3 || (requiresApiBase && (!apiBaseUrl || apiBaseUrl.length < 3)) || isLoadingModels}
                      />
                      <Combobox.IndicatorGroup position="absolute" right="0.5rem" top="50%" transform="translateY(-50%)">
                        <Combobox.Trigger>
                          <FaChevronDown size={16} />
                        </Combobox.Trigger>
                      </Combobox.IndicatorGroup>
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
                  </Field.Root>
                  {isLoadingModels && (
                    <Text fontSize="sm" opacity={0.7} mt={1}>
                      Fetching available models for {currentProvider?.name}...
                    </Text>
                  )}
                  {!isLoadingModels && llmProvider && apiKey && apiKey.length >= 3 && (!requiresApiBase || (apiBaseUrl && apiBaseUrl.length >= 3)) && availableModels.length === 0 && (
                    <Text fontSize="sm" color="red.500" mt={1}>
                      Unable to fetch models. Please check your API key{requiresApiBase ? ' and API base URL' : ''}.
                    </Text>
                  )}
                </Box>
                  {/* Dummy button for layout consistency */}
                <Box><Button visibility="hidden">Add Configuration</Button></Box>
              </HStack>
            </Box>
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