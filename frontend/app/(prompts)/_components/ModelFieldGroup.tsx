'use client';

import React, { useMemo } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Combobox,
  createListCollection,
} from '@chakra-ui/react';
import { Tooltip } from '@/components/ui/tooltip';
import { FaChevronDown } from 'react-icons/fa';
import { LuInfo } from 'react-icons/lu';
import { useCurrentPrompt, usePromptActions } from '@/stores/promptStore/hooks';
import { useConfigStore } from '@/stores/configStore';

export function ModelFieldGroup() {
  const currentPrompt = useCurrentPrompt();
  const { setCurrentPrompt } = usePromptActions();
  const config = useConfigStore(state => state.config);
  const [modelSearchValue, setModelSearchValue] = React.useState('');

  // Build provider/model options from config
  const modelOptions = useMemo(() => {
    const llmConfigs = config.llm_configs || [];
    return llmConfigs.map(llm => ({
      label: `${llm.provider} / ${llm.model}`,
      value: `${llm.provider}:${llm.model}`,
      provider: llm.provider,
      model: llm.model,
    }));
  }, [config.llm_configs]);

  if (!currentPrompt) {
    return null;
  }

  const { prompt } = currentPrompt;
  const currentModelValue = `${prompt.provider}:${prompt.model}`;
  const failoverModelValue = prompt.failover_model || '';

  const filteredModels = modelOptions.filter(opt =>
    opt.label.toLowerCase().includes(modelSearchValue.toLowerCase())
  );

  return (
    <Box>
      <Text fontSize="lg" fontWeight="semibold" mb={4}>
        Model Configuration
      </Text>
      <VStack gap={4} align="stretch">
        <HStack gap={4}>
          {/* Primary Model */}
          <Box flex={1}>
            <HStack mb={2}>
              <Text fontWeight="medium">Primary Model</Text>
              <Tooltip content="Select the primary provider and model used for generating responses.">
                <Box cursor="help">
                  <LuInfo size={14} opacity={0.6} />
                </Box>
              </Tooltip>
            </HStack>
            <Combobox.Root
              collection={createListCollection({
                items: filteredModels.map(opt => ({
                  value: opt.value,
                  label: opt.label
                }))
              })}
              value={[currentModelValue]}
              onValueChange={(e) => {
                const selected = modelOptions.find(opt => opt.value === e.value[0]);
                if (selected) {
                  setCurrentPrompt({
                    ...currentPrompt,
                    prompt: {
                      ...currentPrompt.prompt,
                      provider: selected.provider,
                      model: selected.model,
                    },
                  });
                }
              }}
              inputValue={modelSearchValue}
              onInputValueChange={(e) => setModelSearchValue(e.inputValue)}
              openOnClick
            >
              <Combobox.Control position="relative">
                <Combobox.Input
                  placeholder="Select primary provider and model"
                  paddingRight="2rem"
                />
                <Combobox.Trigger position="absolute" right="0.5rem" top="50%" transform="translateY(-50%)">
                  <FaChevronDown size={16} />
                </Combobox.Trigger>
              </Combobox.Control>
              <Combobox.Positioner>
                <Combobox.Content>
                  {filteredModels.map(opt => (
                    <Combobox.Item key={opt.value} item={opt.value}>
                      <Combobox.ItemText>{opt.label}</Combobox.ItemText>
                      <Combobox.ItemIndicator />
                    </Combobox.Item>
                  ))}
                </Combobox.Content>
              </Combobox.Positioner>
            </Combobox.Root>
          </Box>

          {/* Failover Model */}
          <Box flex={1}>
            <HStack mb={2}>
              <Text fontWeight="medium">Failover Model</Text>
              <Tooltip content="Backup model used if the primary model fails or is unavailable.">
                <Box cursor="help">
                  <LuInfo size={14} opacity={0.6} />
                </Box>
              </Tooltip>
            </HStack>
            <Combobox.Root
              collection={createListCollection({
                items: filteredModels.map(opt => ({
                  value: opt.value,
                  label: opt.label
                }))
              })}
              value={[failoverModelValue]}
              onValueChange={(e) => {
                setCurrentPrompt({
                  ...currentPrompt,
                  prompt: {
                    ...currentPrompt.prompt,
                    failover_model: e.value[0] || '',
                  },
                });
              }}
              inputValue={modelSearchValue}
              onInputValueChange={(e) => setModelSearchValue(e.inputValue)}
              openOnClick
            >
              <Combobox.Control position="relative">
                <Combobox.Input
                  placeholder="Select failover model (optional)"
                  paddingRight="2rem"
                />
                <Combobox.Trigger position="absolute" right="0.5rem" top="50%" transform="translateY(-50%)">
                  <FaChevronDown size={16} />
                </Combobox.Trigger>
              </Combobox.Control>
              <Combobox.Positioner>
                <Combobox.Content>
                  {filteredModels.map(opt => (
                    <Combobox.Item key={opt.value} item={opt.value}>
                      <Combobox.ItemText>{opt.label}</Combobox.ItemText>
                      <Combobox.ItemIndicator />
                    </Combobox.Item>
                  ))}
                </Combobox.Content>
              </Combobox.Positioner>
            </Combobox.Root>
          </Box>
        </HStack>
      </VStack>
    </Box>
  );
}