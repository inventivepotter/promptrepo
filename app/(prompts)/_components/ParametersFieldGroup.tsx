'use client';

import React from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  NumberInput,
} from '@chakra-ui/react';
import { Tooltip } from '@/components/ui/tooltip';
import { LuInfo } from 'react-icons/lu';
import { useColorModeValue } from '@/components/ui/color-mode';
import { Prompt } from '@/types/Prompt';

interface ParametersFieldGroupProps {
  formData: Partial<Prompt>;
  updateField: (field: keyof Prompt, value: string | number | boolean) => void;
  handleTemperatureChange: (value: string) => void;
  handleTopPChange: (value: string) => void;
}

export function ParametersFieldGroup({
  formData,
  updateField,
  handleTemperatureChange,
  handleTopPChange
}: ParametersFieldGroupProps) {
  const mutedTextColor = useColorModeValue('gray.600', 'gray.400');

  return (
    <Box opacity={!formData.repo ? 0.5 : 1}>
      <Text fontSize="lg" fontWeight="semibold" mb={4}>
        Parameters
      </Text>
      <VStack gap={4} align="stretch">
        <HStack gap={4}>
          <Box flex={1}>
            <HStack mb={2}>
              <Text fontWeight={formData.repo ? "medium" : "normal"} color={!formData.repo ? "gray.400" : undefined}>Temperature</Text>
              <Tooltip content="Controls randomness. Higher values (up to 2) make output more creative, lower values more focused.">
                <Box cursor="help">
                  <LuInfo size={14} opacity={0.6} />
                </Box>
              </Tooltip>
            </HStack>
            <NumberInput.Root
              size="sm"
              inputMode="decimal"
              onValueChange={(e) => handleTemperatureChange(e.value)}
              min={0}
              max={2}
              step={0.01}
              value={formData.temperature?.toString() || '0.0'}
            >
              <NumberInput.Input />
              <NumberInput.Control />
            </NumberInput.Root>
          </Box>

          <Box flex={1}>
            <HStack mb={2}>
              <Text fontWeight={formData.repo ? "medium" : "normal"} color={!formData.repo ? "gray.400" : undefined}>Top P (0.00 - 1.00)</Text>
              <Tooltip content="Probability mass for nucleus sampling. Lower values restrict possible outputs, higher values allow more diversity.">
                <Box cursor="help">
                  <LuInfo size={14} opacity={0.6} />
                </Box>
              </Tooltip>
            </HStack>
            <NumberInput.Root
              size="sm"
              inputMode="decimal"
              onValueChange={(e) => handleTopPChange(e.value)}
              min={0}
              max={1}
              step={0.01}
              value={formData.top_p?.toString() || '1.0'}
            >
              <NumberInput.Input />
              <NumberInput.Control />
            </NumberInput.Root>
          </Box>

          <Box flex={1}>
            <HStack mb={2}>
              <Text fontWeight={formData.repo ? "medium" : "normal"} color={!formData.repo ? "gray.400" : undefined}>Max Tokens</Text>
              <Tooltip content="Maximum number of tokens the model can generate in the response.">
                <Box cursor="help">
                  <LuInfo size={14} opacity={0.6} />
                </Box>
              </Tooltip>
            </HStack>
            <NumberInput.Root
              size="sm"
              inputMode="decimal"
              onValueChange={(e) => updateField('max_tokens', parseInt(e.value) || 2048)}
              min={1}
              max={100000}
              step={1}
              value={formData.max_tokens?.toString() || '2048'}
            >
              <NumberInput.Input />
              <NumberInput.Control />
            </NumberInput.Root>
          </Box>
        </HStack>

      </VStack>
    </Box>
  );
}