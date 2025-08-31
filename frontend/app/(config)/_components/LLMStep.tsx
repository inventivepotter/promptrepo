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
import { LLMConfig } from "@/types/Configuration";
import { LLMProvider, LLMProviderModel } from "@/types/LLMProvider";
import { modelsApi } from "../_lib/api/modelsApi";

interface LLMStepProps {
  selectedProvider: string
  setSelectedProvider: (id: string) => void
  selectedModel: string
  setSelectedModel: (id: string) => void
  apiKey: string
  setApiKey: (key: string) => void
  apiBaseUrl: string
  setApiBaseUrl: (url: string) => void
  llmConfigs: LLMConfig[]
  addLLMConfig: () => void
  removeLLMConfig: (index: number) => void
  downloadEnvFile: () => void
  disabled?: boolean
  availableProviders: LLMProvider[]
  isLoadingProviders: boolean
}

export default function LLMStep({
  selectedProvider,
  setSelectedProvider,
  selectedModel,
  setSelectedModel,
  apiKey,
  setApiKey,
  apiBaseUrl,
  setApiBaseUrl,
  llmConfigs,
  addLLMConfig,
  removeLLMConfig,
  disabled = false,
  availableProviders,
  isLoadingProviders,
}: LLMStepProps) {
  const [availableModels, setAvailableModels] = useState<LLMProviderModel[]>([]);
  const [isFetchingModels, setIsFetchingModels] = useState(false);

  // Find the current provider to check if it requires custom API base
  const currentProvider = availableProviders.find(p => p.id === selectedProvider);
  const requiresApiBase = currentProvider?.custom_api_base || false;

  // Fetch models when provider and API key are available
  useEffect(() => {
    const fetchModels = async () => {
      if (!selectedProvider || !apiKey || apiKey.length < 3) {
        setAvailableModels([]);
        return;
      }

      // For providers that require API base, wait until it's provided
      if (requiresApiBase && (!apiBaseUrl || apiBaseUrl.length < 3)) {
        setAvailableModels([]);
        return;
      }

      setIsFetchingModels(true);
      try {
        const result = await modelsApi.fetchModelsByProvider(
          selectedProvider,
          apiKey,
          requiresApiBase ? apiBaseUrl : ''
        );
        if (result.success && result.data && result.data.models && Array.isArray(result.data.models)) {
          setAvailableModels(result.data.models);
        } else {
          console.error('Failed to fetch models:', 'error' in result ? result.error : 'Unknown error');
          setAvailableModels([]);
        }
      } catch (error) {
        console.error('Error fetching models:', error);
        setAvailableModels([]);
      } finally {
        setIsFetchingModels(false);
      }
    };

    // Debounce the API call
    const timeoutId = setTimeout(fetchModels, 500);
    return () => clearTimeout(timeoutId);
  }, [selectedProvider, apiKey, apiBaseUrl, requiresApiBase]);

  // Clear selected model when provider changes
  const handleProviderChange = (newProvider: string) => {
    setSelectedProvider(newProvider);
    if (newProvider !== selectedProvider) {
      setSelectedModel('');
      setAvailableModels([]);
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
                      items: (Array.isArray(availableProviders) ? availableProviders : []).map((p: LLMProvider) => ({ label: p.name, value: p.id }))
                    })}
                    value={[selectedProvider]}
                    onValueChange={(e) => {
                      const newProvider = e.value?.[0] || '';
                      handleProviderChange(newProvider);
                    }}
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
                        {(Array.isArray(availableProviders) ? availableProviders : []).map((provider: LLMProvider) => (
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
                    value={apiKey || ''}
                    onChange={(e) => setApiKey(e.target.value)}
                    disabled={disabled || !selectedProvider}
                  />
                </Box>
              </HStack>
              <Text fontSize="sm" opacity={0.7} mt={2}>
                Both provider and API key are required to fetch available models.
              </Text>
            </Box>

            {/* Step 1.5: API Base URL (conditional) */}
            {selectedProvider && requiresApiBase && (
              <Box width="100%">
                <Text mb={2} fontWeight="medium">API Base URL</Text>
                <Input
                  placeholder="Enter API base URL (e.g., http://localhost:1234/v1)"
                  value={apiBaseUrl || ''}
                  onChange={(e) => setApiBaseUrl(e.target.value)}
                  disabled={disabled}
                />
                <Text fontSize="sm" opacity={0.7} mt={1}>
                  Custom API endpoint for {currentProvider?.name}
                </Text>
              </Box>
            )}

            {/* Step 2: Select Model (after provider, API key, and API base URL if required are entered) */}
            {selectedProvider && apiKey && apiKey.length >= 3 && (!requiresApiBase || (apiBaseUrl && apiBaseUrl.length >= 3)) && (
              <Box width="100%">
                <Text mb={2} fontWeight="medium">2. Model</Text>
                <Combobox.Root
                  collection={createListCollection({
                    items: (Array.isArray(availableModels) ? availableModels : []).map((m: LLMProviderModel) => ({ label: m.name, value: m.id }))
                  })}
                  value={[selectedModel]}
                  onValueChange={(e) => setSelectedModel(e.value[0] || '')}
                  openOnClick
                  disabled={disabled || isFetchingModels}
                >
                  <Combobox.Control position="relative">
                    <Combobox.Input
                      placeholder={isFetchingModels ? "Fetching models..." : "Select model"}
                      paddingRight="2rem"
                      disabled={disabled || isFetchingModels}
                    />
                    <Combobox.Trigger position="absolute" right="0.5rem" top="50%" transform="translateY(-50%)">
                      <FaChevronDown size={16} />
                    </Combobox.Trigger>
                  </Combobox.Control>
                  <Combobox.Positioner>
                    <Combobox.Content>
                      {(Array.isArray(availableModels) ? availableModels : []).map((model: LLMProviderModel) => (
                        <Combobox.Item key={model.id} item={model.id}>
                          <Combobox.ItemText>{model.name}</Combobox.ItemText>
                          <Combobox.ItemIndicator />
                        </Combobox.Item>
                      ))}
                    </Combobox.Content>
                  </Combobox.Positioner>
                </Combobox.Root>
                {isFetchingModels && (
                  <Text fontSize="sm" opacity={0.7} mt={1}>
                    Fetching available models for {(Array.isArray(availableProviders) ? availableProviders : []).find((p: LLMProvider) => p.id === selectedProvider)?.name}...
                  </Text>
                )}
                {!isFetchingModels && availableModels.length === 0 && apiKey && apiKey.length >= 3 && (!requiresApiBase || (apiBaseUrl && apiBaseUrl.length >= 3)) && (
                  <Text fontSize="sm" color="red.500" mt={1}>
                    Unable to fetch models. Please check your API key{requiresApiBase ? ' and API base URL' : ''}.
                  </Text>
                )}
              </Box>
            )}
            
            <Button
              onClick={addLLMConfig}
              disabled={
                !selectedProvider ||
                !selectedModel ||
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
              {llmConfigs.map((config, index) => (
                <HStack key={index} justify="space-between" width="100%" p={2} bg="bg.subtle" borderRadius="md">
                  <Text fontSize="sm" fontWeight="400">
                    Provider: <Text as="span" fontWeight="bold">{config.provider}</Text> | Model: <Text as="span" fontWeight="bold">{config.model}</Text>
                    {config.apiBaseUrl && (
                      <> | API Base: <Text as="span" fontWeight="bold">{config.apiBaseUrl}</Text></>
                    )}
                  </Text>
                  <Button
                    size="sm"
                    onClick={() => removeLLMConfig(index)}
                    disabled={disabled}
                  >
                    Remove
                  </Button>
                </HStack>
              ))}
            </VStack>
          </Box>
        )}
      </VStack>
    </Box>
  )
}