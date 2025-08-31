'use client';

import React from 'react';
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
import { Prompt } from '@/types/Prompt';
import { LLMProvider } from '@/types/LLMProvider';

interface ModelFieldGroupProps {
  formData: Partial<Prompt>;
  configuredModels: Array<LLMProvider>;
  updateField: (field: keyof Prompt, value: string | number | boolean) => void;
}

export function ModelFieldGroup({
  formData,
  configuredModels,
  updateField
}: ModelFieldGroupProps) {
  const [primaryModelSearchValue, setPrimaryModelSearchValue] = React.useState('');
  const [failoverModelSearchValue, setFailoverModelSearchValue] = React.useState('');

  // Filter models based on search values
  const filteredModelsForPrimary = configuredModels.filter(model =>
    model.name.toLowerCase().includes(primaryModelSearchValue.toLowerCase()) ||
    model.id.toLowerCase().includes(primaryModelSearchValue.toLowerCase())
  );

  const filteredModelsForFailover = configuredModels.filter(model =>
    model.name.toLowerCase().includes(failoverModelSearchValue.toLowerCase()) ||
    model.id.toLowerCase().includes(failoverModelSearchValue.toLowerCase())
  );

  return (
    <Box opacity={!formData.repo ? 0.5 : 1}>
      <Text fontSize="lg" fontWeight="semibold" mb={4}>
        Model Configuration
      </Text>
      <VStack gap={4} align="stretch">
        <HStack gap={4}>
          <Box flex={1}>
            <HStack mb={2}>
              <Text fontWeight={formData.repo ? "medium" : "normal"} color={!formData.repo ? "gray.400" : undefined}>Primary Model</Text>
              <Tooltip content="Select the main model used for generating responses.">
                <Box cursor="help">
                  <LuInfo size={14} opacity={0.6} />
                </Box>
              </Tooltip>
            </HStack>
            <Combobox.Root
              collection={createListCollection({
                items: filteredModelsForPrimary.map(model => ({
                  value: model.id,
                  label: model.name
                }))
              })}
              value={[formData.model || '']}
              onValueChange={(e) => updateField('model', e.value[0] || '')}
              inputValue={primaryModelSearchValue}
              onInputValueChange={(e) => setPrimaryModelSearchValue(e.inputValue)}
              openOnClick
            >
              <Combobox.Control position="relative">
                <Combobox.Input
                  placeholder="Select primary model"
                  paddingRight="2rem"
                />
                <Combobox.Trigger position="absolute" right="0.5rem" top="50%" transform="translateY(-50%)">
                  <FaChevronDown size={16} />
                </Combobox.Trigger>
              </Combobox.Control>
              <Combobox.Positioner>
                <Combobox.Content>
                  {filteredModelsForPrimary.map(model => (
                    <Combobox.Item key={model.id} item={model.id}>
                      <Combobox.ItemText>{model.name}</Combobox.ItemText>
                      <Combobox.ItemIndicator />
                    </Combobox.Item>
                  ))}
                </Combobox.Content>
              </Combobox.Positioner>
            </Combobox.Root>
          </Box>

          <Box flex={1}>
            <HStack mb={2}>
              <Text fontWeight={formData.repo ? "medium" : "normal"} color={!formData.repo ? "gray.400" : undefined}>Failover Model</Text>
              <Tooltip content="Backup model used if the primary model fails or is unavailable.">
                <Box cursor="help">
                  <LuInfo size={14} opacity={0.6} />
                </Box>
              </Tooltip>
            </HStack>
            <Combobox.Root
              collection={createListCollection({
                items: filteredModelsForFailover.map(model => ({
                  value: model.id,
                  label: model.name
                }))
              })}
              value={[formData.failover_model || '']}
              onValueChange={(e) => updateField('failover_model', e.value[0] || '')}
              inputValue={failoverModelSearchValue}
              onInputValueChange={(e) => setFailoverModelSearchValue(e.inputValue)}
              openOnClick
            >
              <Combobox.Control position="relative">
                <Combobox.Input
                  placeholder="Select failover model"
                  paddingRight="2rem"
                />
                <Combobox.Trigger position="absolute" right="0.5rem" top="50%" transform="translateY(-50%)">
                  <FaChevronDown size={16} />
                </Combobox.Trigger>
              </Combobox.Control>
              <Combobox.Positioner>
                <Combobox.Content>
                  {filteredModelsForFailover.map(model => (
                    <Combobox.Item key={model.id} item={model.id}>
                      <Combobox.ItemText>{model.name}</Combobox.ItemText>
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