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
import { useColorModeValue } from '@/components/ui/color-mode';
import { Prompt } from '@/types/Prompt';

interface ModelFieldGroupProps {
  formData: Partial<Prompt>;
  modelCollection: ReturnType<typeof createListCollection<{ value: string; label: string }>>;
  updateField: (field: keyof Prompt, value: string | number | boolean) => void;
}

export function ModelFieldGroup({
  formData,
  modelCollection,
  updateField
}: ModelFieldGroupProps) {
  const mutedTextColor = useColorModeValue('gray.600', 'gray.400');

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
              collection={modelCollection}
              value={[formData.model || '']}
              onValueChange={(e) => updateField('model', e.value[0] || '')}
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
                  {modelCollection.items.map((option) => (
                    <Combobox.Item key={option.value} item={option.value}>
                      <Combobox.ItemText>{option.label}</Combobox.ItemText>
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
              collection={modelCollection}
              value={[formData.failover_model || '']}
              onValueChange={(e) => updateField('failover_model', e.value[0] || '')}
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
                  {modelCollection.items.map((option) => (
                    <Combobox.Item key={option.value} item={option.value}>
                      <Combobox.ItemText>{option.label}</Combobox.ItemText>
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