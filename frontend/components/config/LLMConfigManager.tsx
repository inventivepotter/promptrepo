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
  Card,
  Fieldset,
  Stack,
  Skeleton,
  EmptyState,
  Collapsible,
} from '@chakra-ui/react'
import { LuCpu, LuChevronDown, LuChevronUp } from 'react-icons/lu';
import { useEffect, useState } from 'react';
import type { components } from '@/types/generated/api';
import { useConfig, useConfigActions, useAvailableProviders, useLLMFormState, useLLMFormUIState, useConfigStore, useIsLoadingConfig, useIsSavingRepo } from '@/stores/configStore';

type LLMConfig = components['schemas']['LLMConfig'];
type BasicProviderInfo = components['schemas']['BasicProviderInfo'];
type ModelInfo = components['schemas']['ModelInfo'];

interface LLMConfigManagerProps {
  disabled?: boolean
}

export default function LLMConfigManager({
  disabled = false
}: LLMConfigManagerProps) {
  const [showLLMConfig, setShowLLMConfig] = useState(true);
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
    setIsSaving,
  } = useConfigActions();
  const availableProviders = useAvailableProviders();
  const { llmProvider, apiKey, llmModel, apiBaseUrl, availableModels, isLoadingModels } = useLLMFormState();
  const { providerSearchValue, modelSearchValue } = useLLMFormUIState();
  const isSaving = useIsSavingRepo();
  const isLoading = useIsLoadingConfig();
  
  const llmConfigs = config.llm_configs || [];
  const borderColor = "bg.muted";
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

  // Fetch models when API key or API base URL changes (debounced for API base URL)
  useEffect(() => {
    if (llmProvider && apiKey && apiKey.length >= 3 && (!requiresApiBase || (apiBaseUrl && apiBaseUrl.length >= 3))) {
      // Debounce only when requiresApiBase is true and apiBaseUrl is changing
      const timeoutId = setTimeout(() => {
        fetchModelsIfReady();
      }, requiresApiBase ? 500 : 0);

      return () => clearTimeout(timeoutId);
    }
  }, [apiKey, apiBaseUrl, llmProvider, requiresApiBase, fetchModelsIfReady]);

  const handleAddConfiguration = async () => {
    const newConfig: LLMConfig = {
      id: '',
      provider: llmProvider,
      model: llmModel,
      api_key: apiKey,
      api_base_url: requiresApiBase ? apiBaseUrl : '',
      scope: 'user',
      label: '',
    };
    
    addLLMConfig(newConfig);
    
    // Update config to persist to backend
    const updatedConfig = {
      ...config,
      llm_configs: [...(config.llm_configs || []), newConfig]
    };
    
    try {
      setIsSaving(true);
      await updateConfig(updatedConfig);
      
      // Reset form
      resetLLMForm();
      setProviderSearchValue('');
      setModelSearchValue('');
    } catch (error) {
      console.error('Error saving configuration:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleRemoveConfig = async (index: number) => {
    // removeLLMConfig already updates the state correctly.
    // We just need to call updateConfig to persist the current state.
    removeLLMConfig(index);
    
    try {
      // Get the latest state directly from the store after the removal
      const currentState = useConfigStore.getState().config;
      await updateConfig(currentState);
    } catch (error) {
      console.error('Error removing configuration:', error);
    }
  };

  return (
    <Card.Root
      id="llm-config"
      borderWidth="1px"
      borderColor={borderColor}
      overflow="visible"
    >
      <Card.Body p={8} overflow="visible">
        <Fieldset.Root size="lg" overflow="visible">
          <HStack justify="space-between" align="center">
            <Stack flex={1}>
              <Fieldset.Legend>LLM Provider Configuration</Fieldset.Legend>
              <Fieldset.HelperText color="text.tertiary">
                Setup your AI provider and API key first, then select from available models.
              </Fieldset.HelperText>
            </Stack>
            <Button
              variant="ghost"
              _hover={{ bg: "bg.subtle" }}
              size="sm"
              onClick={() => setShowLLMConfig(!showLLMConfig)}
              aria-label={showLLMConfig ? "Collapse LLM configuration" : "Expand LLM configuration"}
            >
              <HStack gap={1}>
                <Text fontSize="xs" fontWeight="medium">
                  {showLLMConfig ? "Hide" : "Show"}
                </Text>
                {showLLMConfig ? <LuChevronUp /> : <LuChevronDown />}
              </HStack>
            </Button>
          </HStack>

          <Fieldset.Content overflow="visible">
            <Collapsible.Root open={showLLMConfig}>
              <Collapsible.Content overflow="visible">
                <VStack gap={6} align="stretch" mt={3}>
        {/* Add new LLM configuration */}
        <Card.Root
          bg="transparent"
          borderWidth="1px"
          borderColor={borderColor}
          overflow="visible"
        >
          <Card.Body p={8} overflow="visible">
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
                          <LuChevronDown size={16} />
                        </Combobox.Trigger>
                      </Combobox.IndicatorGroup>
                    </Combobox.Control>
                    <Combobox.Positioner style={{ zIndex: 40 }}>
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
                      disabled ||
                      isSaving
                    }
                    loading={isSaving}
                    loadingText="Saving..."
                    alignSelf="end"
                    verticalAlign={"bottom"}
                  >
                    Add LLM Config
                  </Button>
                </Box>
              </HStack>
            </Box>

            {/* Step 1.5: API Base URL, Model, and other fields */}
            <Box width="100%">
              <HStack gap={4} width="100%" align="start">
                {requiresApiBase && (
                  <Box flex={2.4}>
                    <Field.Root required>
                      <Field.Label>API Base URL <Field.RequiredIndicator /></Field.Label>
                      <Input
                        placeholder="Enter API base URL (e.g., http://localhost:1234/v1)"
                        value={apiBaseUrl}
                        onChange={(e) => setApiBaseUrl(e.target.value)}
                        disabled={disabled || !llmProvider}
                        width="100%"
                      />
                    </Field.Root>
                  </Box>
                )}
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
                          <LuChevronDown size={16} />
                        </Combobox.Trigger>
                      </Combobox.IndicatorGroup>
                    </Combobox.Control>
                    <Combobox.Positioner style={{ zIndex: 40 }}>
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
                <Box><Button visibility="hidden">Add LLM Config</Button></Box>
              </HStack>
            </Box>
          </VStack>
          </Card.Body>
        </Card.Root>
        {/* Display configured LLMs */}
        {llmConfigs.length > 0 || isLoading ? (
          <Card.Root
            borderWidth="1px"
            borderColor={borderColor}
            bg="transparent"
          >
            <Card.Body p={8}>
              <Text fontWeight="semibold" fontSize="lg" mb={6}>Configured LLM Providers</Text>
              {isLoading ? (
                <VStack gap={4} width="100%">
                  {[1, 2, 3].map((i) => (
                    <Skeleton key={i} height="80px" width="100%" bg="bg"/>
                  ))}
                </VStack>
              ) : (
                <VStack gap={4}>
              {llmConfigs.map((config, index) => {
                const isOrgScope = config.scope === 'organization';
                return (
                  <Card.Root
                    key={index}
                    width="100%"
                    bg="bg.panel"
                    borderWidth="1px"
                    borderColor="bg.muted"
                    transition="all 0.2s"
                    _hover={{
                      borderColor: "bg.muted",
                      shadow: "sm"
                    }}
                  >
                    <Card.Body p={5}>
                      <HStack justify="space-between" width="100%">
                        <HStack gap={3} flex={1}>
                          <Box minWidth="70px" pr={2}>
                            <Text fontSize="xs" color="fg.muted" mb={1}>Provider</Text>
                            <Text fontSize="sm" fontWeight="semibold">{config.provider}</Text>
                          </Box>
                          <Box height="40px" width="1px" bg="border.subtle" />
                          <Box px={2}>
                            <Text fontSize="xs" color="fg.muted" mb={1}>Model</Text>
                            <Text fontSize="sm" fontWeight="semibold">{config.model}</Text>
                          </Box>
                          {!isOrgScope && config.api_base_url && (
                            <>
                              <Box height="40px" width="1px" bg="border.subtle" />
                              <Box px={2}>
                                <Text fontSize="xs" color="fg.muted" mb={1}>API Base</Text>
                                <Text
                                  fontSize="sm"
                                  fontWeight="medium"
                                  maxWidth="200px"
                                  overflow="hidden"
                                  textOverflow="ellipsis"
                                  whiteSpace="nowrap"
                                >
                                  {config.api_base_url}
                                </Text>
                              </Box>
                            </>
                          )}
                        </HStack>
                        <HStack gap={3}>
                          {isOrgScope && (
                            <Box
                              px={2}
                              py={1}
                              bg="bg.subtle"
                              borderRadius="sm"
                              borderWidth="1px"
                              borderColor="border.subtle"
                            >
                              <Text fontSize="xs" fontWeight="normal" color="fg.muted">
                                {config.label || "Organization Scoped"}
                              </Text>
                            </Box>
                          )}
                          <Button
                            size="sm"
                            variant="outline"
                            colorScheme="red"
                            onClick={() => handleRemoveConfig(index)}
                            disabled={disabled || isOrgScope}
                            opacity={isOrgScope ? 0.5 : 1}
                          >
                            Remove
                          </Button>
                        </HStack>
                      </HStack>
                    </Card.Body>
                  </Card.Root>
                );
              })}
                </VStack>
              )}
            </Card.Body>
          </Card.Root>
        ) : (
          <Card.Root
            borderWidth="1px"
            borderColor={borderColor}
            bg="transparent"
          >
            <Card.Body p={8}>
              <EmptyState.Root>
                <EmptyState.Content>
                  <EmptyState.Indicator>
                    <LuCpu />
                  </EmptyState.Indicator>
                  <VStack textAlign="center">
                    <EmptyState.Title>No LLM providers configured</EmptyState.Title>
                    <EmptyState.Description>
                      Add your first LLM provider to get started
                    </EmptyState.Description>
                  </VStack>
                </EmptyState.Content>
              </EmptyState.Root>
            </Card.Body>
          </Card.Root>
        )}
                </VStack>
              </Collapsible.Content>
            </Collapsible.Root>
          </Fieldset.Content>
        </Fieldset.Root>
      </Card.Body>
    </Card.Root>
  )
}
