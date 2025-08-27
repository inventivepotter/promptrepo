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
import React from "react";
import { FaChevronDown } from 'react-icons/fa';
import { getAvailableModels } from '../_lib/getAvailableModels';
import { LLMConfig } from "@/types/Configuration";
import { LLMProvider } from "@/types/LLMProvider";

interface LLMStepProps {
  selectedProvider: string
  setSelectedProvider: (id: string) => void
  selectedModel: string
  setSelectedModel: (id: string) => void
  apiKey: string
  setApiKey: (key: string) => void
  llmConfigs: LLMConfig[]
  addLLMConfig: () => void
  removeLLMConfig: (index: number) => void
  downloadEnvFile: () => void
  disabled?: boolean
}

export default function LLMStep({
  selectedProvider,
  setSelectedProvider,
  selectedModel,
  setSelectedModel,
  apiKey,
  setApiKey,
  llmConfigs,
  addLLMConfig,
  removeLLMConfig,
  disabled = false,
}: LLMStepProps) {
  const providers: LLMProvider[] = getAvailableModels();

  return (
    <Box p={6} borderWidth="1px" borderRadius="md" borderColor="border.emphasized">
      <VStack gap={6} align="stretch">
        <Text fontSize="lg" fontWeight="bold">LLM Provider Configuration</Text>
        <Text fontSize="sm" opacity={0.7} mb={2}>
          Setup your AI provider and model to enable intelligent features in your application.
        </Text>
        {/* Add new LLM configuration */}
        <Box p={6} borderWidth="1px" borderRadius="md" borderColor="border.muted">
          <VStack gap={4}>
            <Box width="100%">
              <Text mb={2} fontWeight="medium">LLM Provider</Text>
              <Combobox.Root
                collection={createListCollection({
                  items: providers.map(p => ({ label: p.name, value: p.id }))
                })}
                value={[selectedProvider]}
                onValueChange={(e) => {
                  const newProvider = e.value?.[0] || '';
                  setSelectedProvider(newProvider);
                  if (newProvider !== selectedProvider) {
                    setSelectedModel('');
                  }
                }}
                openOnClick
                disabled={disabled}
              >
                <Combobox.Control position="relative">
                  <Combobox.Input
                    placeholder="Select or search provider"
                    paddingRight="2rem"
                    disabled={disabled}
                  />
                  <Combobox.Trigger position="absolute" right="0.5rem" top="50%" transform="translateY(-50%)">
                    <FaChevronDown size={16} />
                  </Combobox.Trigger>
                </Combobox.Control>
                <Combobox.Positioner>
                  <Combobox.Content>
                    {providers.map(provider => (
                      <Combobox.Item key={provider.id} item={provider.id}>
                        <Combobox.ItemText>{provider.name}</Combobox.ItemText>
                        <Combobox.ItemIndicator />
                      </Combobox.Item>
                    ))}
                  </Combobox.Content>
                </Combobox.Positioner>
              </Combobox.Root>
            </Box>
            {selectedProvider && (
              <Box width="100%">
                <Text mb={2} fontWeight="medium">Model</Text>
                <Combobox.Root
                  collection={createListCollection({
                    items: (providers.find(p => p.id === selectedProvider)?.models || []).map(m => ({ label: m.name, value: m.id }))
                  })}
                  value={[selectedModel]}
                  onValueChange={(e) => setSelectedModel(e.value[0] || '')}
                  openOnClick
                  disabled={disabled}
                >
                  <Combobox.Control position="relative">
                    <Combobox.Input
                      placeholder="Select or search model"
                      paddingRight="2rem"
                      disabled={disabled}
                    />
                    <Combobox.Trigger position="absolute" right="0.5rem" top="50%" transform="translateY(-50%)">
                      <FaChevronDown size={16} />
                    </Combobox.Trigger>
                  </Combobox.Control>
                  <Combobox.Positioner>
                    <Combobox.Content>
                      {providers.find(p => p.id === selectedProvider)?.models.map(model => (
                        <Combobox.Item key={model.id} item={model.id}>
                          <Combobox.ItemText>{model.name}</Combobox.ItemText>
                          <Combobox.ItemIndicator />
                        </Combobox.Item>
                      ))}
                    </Combobox.Content>
                  </Combobox.Positioner>
                </Combobox.Root>
              </Box>
            )}
            {selectedModel && (
              <Box width="100%">
                <Text mb={2} fontWeight="medium">API Key</Text>
                <Input
                  type="password"
                  placeholder="Enter API key"
                  value={apiKey || ''}
                  onChange={(e) => setApiKey(e.target.value)}
                  disabled={disabled}
                />
              </Box>
            )}
            <Button
              onClick={addLLMConfig}
              disabled={!selectedProvider || !selectedModel || !apiKey || disabled}
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
                    {providers.find(p => p.id === config.provider)?.name} - {config.model}
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