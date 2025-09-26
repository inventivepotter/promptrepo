'use client';

import { useState } from 'react';
import { 
  Box, 
  VStack, 
  HStack, 
  Text, 
  Button, 
  Input, 
  IconButton
} from '@chakra-ui/react';
import { LuPlus, LuTrash2 } from 'react-icons/lu';
import { 
  useConfig, 
  useAvailableProviders, 
  useConfigActions
} from '@/stores/configStore';
import type { BasicProviderInfo } from '@/stores/configStore';

interface LLMConfigManagerProps {
  disabled?: boolean;
}

export const LLMConfigManager = ({ disabled = false }: LLMConfigManagerProps) => {
  const config = useConfig();
  const availableProviders = useAvailableProviders();
  const { addLLMConfig, removeLLMConfig } = useConfigActions();
  
  const [newProvider, setNewProvider] = useState<string>('');
  const [newApiKey, setNewApiKey] = useState<string>('');

  const handleAddLLMConfig = () => {
    if (!newProvider || !newApiKey.trim()) return;

    const selectedProvider = availableProviders.find(p => p.name === newProvider);
    if (!selectedProvider) return;

    const newConfig = {
      id: '', // Blank for new record
      provider: selectedProvider.name,
      model: '', // Will be set later
      api_key: newApiKey.trim(),
      api_base_url: '',
      scope: 'user' as const
    };

    addLLMConfig(newConfig);
    setNewProvider('');
    setNewApiKey('');
  };

  const handleRemoveLLMConfig = (providerId: string) => {
    removeLLMConfig(providerId);
  };

  const getAvailableProvidersForSelection = (): BasicProviderInfo[] => {
    const configuredProviders = config.llm_configs?.map(c => c.provider) || [];
    return availableProviders.filter(p => !configuredProviders.includes(p.name));
  };

  return (
    <Box p={6} borderWidth="1px" borderRadius="md" borderColor="border.emphasized">
      <VStack gap={6} align="stretch">
        <Text fontSize="xl" fontWeight="bold">LLM Configuration</Text>
        <Text fontSize="sm" opacity={0.7}>
          Configure your AI providers and API keys
        </Text>

        {/* Existing Configurations */}
        {config.llm_configs && config.llm_configs.length > 0 && (
          <VStack gap={3} align="stretch">
            <Text fontSize="md" fontWeight="semibold">Configured Providers</Text>
            {config.llm_configs.map((llmConfig, index) => (
              <HStack 
                key={llmConfig.id || index}
                p={3}
                bg="gray.50"
                borderRadius="md"
                justify="space-between"
              >
                <VStack align="flex-start" gap={1}>
                  <Text fontWeight="medium">{llmConfig.provider}</Text>
                  <Text fontSize="sm" opacity={0.7}>
                    Model: {llmConfig.model || 'Not configured'}
                  </Text>
                  <Text fontSize="sm" opacity={0.7}>
                    Scope: {llmConfig.scope}
                  </Text>
                </VStack>
                <IconButton
                  aria-label={`Remove ${llmConfig.provider}`}
                  onClick={() => handleRemoveLLMConfig(llmConfig.id || index.toString())}
                  disabled={disabled}
                  size="sm"
                  variant="ghost"
                  colorScheme="red"
                >
                  <LuTrash2 />
                </IconButton>
              </HStack>
            ))}
          </VStack>
        )}

        {/* Add New Configuration */}
        <VStack gap={4} align="stretch">
          <Text fontSize="md" fontWeight="semibold">Add New Provider</Text>
          
          {getAvailableProvidersForSelection().length === 0 ? (
            <Text fontSize="sm" color="gray.500">
              All available providers have been configured
            </Text>
          ) : (
            <>
              <select
                value={newProvider}
                onChange={(e) => setNewProvider(e.target.value)}
                disabled={disabled}
                style={{
                  padding: '8px 12px',
                  borderRadius: '6px',
                  border: '1px solid #e2e8f0',
                  backgroundColor: 'white'
                }}
              >
                <option value="">Select a provider</option>
                {getAvailableProvidersForSelection().map((provider) => (
                  <option key={provider.name} value={provider.name}>
                    {provider.name}
                  </option>
                ))}
              </select>

              <Input
                placeholder="API Key"
                type="password"
                value={newApiKey}
                onChange={(e) => setNewApiKey(e.target.value)}
                disabled={disabled}
              />

              <Button
                onClick={handleAddLLMConfig}
                disabled={disabled || !newProvider || !newApiKey.trim()}
                colorScheme="blue"
              >
                <LuPlus style={{ marginRight: '8px' }} />
                Add Provider
              </Button>
            </>
          )}
        </VStack>
      </VStack>
    </Box>
  );
};