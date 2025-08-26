'use client';

import React from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  NumberInput,
  Switch,
} from '@chakra-ui/react';
import { Tooltip } from '@/components/ui/tooltip';
import { LuInfo } from 'react-icons/lu';
import { useColorModeValue } from '@/components/ui/color-mode';
import { Prompt } from '../_state/promptState';

interface EnableThinkingFieldGroupProps {
  formData: Partial<Prompt>;
  updateField: (field: keyof Prompt, value: string | number | boolean) => void;
}

export function EnableThinkingFieldGroup({
  formData,
  updateField
}: EnableThinkingFieldGroupProps) {
  const mutedTextColor = useColorModeValue('gray.600', 'gray.400');

  return (
    <VStack gap={4} align="stretch">
      <HStack justify="space-between" align="center">
        <VStack align="start" gap={1}>
          <HStack>
            <Text fontWeight={formData.repo ? "medium" : "normal"} color={!formData.repo ? "gray.400" : undefined}>Enable Thinking</Text>
            <Tooltip content="Allows the model to reason step by step for more complex tasks.">
              <Box cursor="help">
                <LuInfo size={14} opacity={0.6} />
              </Box>
            </Tooltip>
          </HStack>
          <Text fontSize="sm" color={!formData.repo ? "gray.400" : mutedTextColor}>
            Allow the model to think through problems step by step
          </Text>
        </VStack>
        <Switch.Root
          checked={formData.thinking_enabled || false}
          onCheckedChange={(e: { checked: boolean }) => updateField('thinking_enabled', e.checked)}
          size="lg"
        >
          <Switch.HiddenInput />
          <Switch.Control>
            <Switch.Thumb />
          </Switch.Control>
          <Switch.Label />
        </Switch.Root>
      </HStack>

      {formData.thinking_enabled && (
        <Box>
          <HStack mb={2}>
            <Text fontWeight={formData.repo ? "medium" : "normal"} color={!formData.repo ? "gray.400" : undefined}>Thinking Budget</Text>
            <Tooltip content="Limits the number of tokens the model can use for step-by-step reasoning.">
              <Box cursor="help">
                <LuInfo size={14} opacity={0.6} />
              </Box>
            </Tooltip>
          </HStack>
          <NumberInput.Root
            size="sm"
            inputMode="decimal"
            onValueChange={(e) => updateField('thinking_budget', parseInt(e.value) || 20000)}
            min={1000}
            max={100000}
            step={1000}
            value={formData.thinking_budget?.toString() || '20000'}
          >
            <NumberInput.Input />
            <NumberInput.Control />
          </NumberInput.Root>
        </Box>
      )}
    </VStack>
  );
}