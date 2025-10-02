'use client';

import {
  Box,
  VStack,
  HStack,
  Text,
  NumberInput,
  Switch,
  Field,
  Input,
} from '@chakra-ui/react';
import { Tooltip } from '@/components/ui/tooltip';
import { LuInfo } from 'react-icons/lu';
import { useCurrentPrompt, useUpdateCurrentPromptField } from '@/stores/promptStore/hooks';

export function ParametersFieldGroup() {
  const currentPrompt = useCurrentPrompt();
  const updateField = useUpdateCurrentPromptField();

  if (!currentPrompt) {
    return null;
  }

  const { prompt } = currentPrompt;

  return (
    <Box>
      <Text fontSize="lg" fontWeight="semibold" mb={4}>
        Parameters
      </Text>
      <VStack gap={4} align="stretch">
        {/* Temperature, Top P, Max Tokens */}
        <HStack gap={4}>
          <Field.Root flex={1}>
            <Field.Label display="flex" alignItems="center" gap={1}>
              Temperature
              <Tooltip content="Controls randomness. Higher values (up to 2) make output more creative, lower values more focused.">
                <Box cursor="help">
                  <LuInfo size={14} opacity={0.6} />
                </Box>
              </Tooltip>
            </Field.Label>
            <NumberInput.Root
              size="sm"
              inputMode="decimal"
              onValueChange={(e) => updateField('temperature', parseFloat(e.value))}
              min={0}
              max={2}
              step={0.01}
              value={prompt.temperature?.toString() || '0.0'}
            >
              <NumberInput.Input />
              <NumberInput.Control />
            </NumberInput.Root>
          </Field.Root>

          <Field.Root flex={1}>
            <Field.Label display="flex" alignItems="center" gap={1}>
              Top P
              <Tooltip content="Probability mass for nucleus sampling. Lower values restrict possible outputs, higher values allow more diversity.">
                <Box cursor="help">
                  <LuInfo size={14} opacity={0.6} />
                </Box>
              </Tooltip>
            </Field.Label>
            <NumberInput.Root
              size="sm"
              inputMode="decimal"
              onValueChange={(e) => updateField('top_p', parseFloat(e.value))}
              min={0}
              max={1}
              step={0.01}
              value={prompt.top_p?.toString() || '1.0'}
            >
              <NumberInput.Input />
              <NumberInput.Control />
            </NumberInput.Root>
          </Field.Root>

          <Field.Root flex={1}>
            <Field.Label display="flex" alignItems="center" gap={1}>
              Max Tokens
              <Tooltip content="Maximum number of tokens the model can generate in the response.">
                <Box cursor="help">
                  <LuInfo size={14} opacity={0.6} />
                </Box>
              </Tooltip>
            </Field.Label>
            <NumberInput.Root
              size="sm"
              inputMode="decimal"
              onValueChange={(e) => updateField('max_tokens', parseInt(e.value) || 2048)}
              min={1}
              max={100000}
              step={1}
              value={prompt.max_tokens?.toString() || '2048'}
            >
              <NumberInput.Input />
              <NumberInput.Control />
            </NumberInput.Root>
          </Field.Root>
        </HStack>

        {/* Additional Parameters */}
        <HStack gap={4}>
          <Field.Root flex={1}>
            <Field.Label display="flex" alignItems="center" gap={1}>
              Presence Penalty
              <Tooltip content="Penalizes new tokens based on whether they appear in the text so far.">
                <Box cursor="help">
                  <LuInfo size={14} opacity={0.6} />
                </Box>
              </Tooltip>
            </Field.Label>
            <NumberInput.Root
              size="sm"
              inputMode="decimal"
              onValueChange={(e) => updateField('presence_penalty', parseFloat(e.value))}
              min={-2}
              max={2}
              step={0.1}
              value={prompt.presence_penalty?.toString() || '0.0'}
            >
              <NumberInput.Input />
              <NumberInput.Control />
            </NumberInput.Root>
          </Field.Root>

          <Field.Root flex={1}>
            <Field.Label display="flex" alignItems="center" gap={1}>
              Frequency Penalty
              <Tooltip content="Penalizes new tokens based on their frequency in the text so far.">
                <Box cursor="help">
                  <LuInfo size={14} opacity={0.6} />
                </Box>
              </Tooltip>
            </Field.Label>
            <NumberInput.Root
              size="sm"
              inputMode="decimal"
              onValueChange={(e) => updateField('frequency_penalty', parseFloat(e.value))}
              min={-2}
              max={2}
              step={0.1}
              value={prompt.frequency_penalty?.toString() || '0.0'}
            >
              <NumberInput.Input />
              <NumberInput.Control />
            </NumberInput.Root>
          </Field.Root>

          <Field.Root flex={1}>
            <Field.Label display="flex" alignItems="center" gap={1}>
              Seed
              <Tooltip content="Random seed for reproducible outputs.">
                <Box cursor="help">
                  <LuInfo size={14} opacity={0.6} />
                </Box>
              </Tooltip>
            </Field.Label>
            <NumberInput.Root
              size="sm"
              onValueChange={(e) => updateField('seed', parseInt(e.value))}
              value={prompt.seed?.toString() || ''}
            >
              <NumberInput.Input placeholder="e.g., 12345" />
              <NumberInput.Control />
            </NumberInput.Root>
          </Field.Root>
        </HStack>

        <HStack gap={4}>
            {/* Max Completion Tokens */}
            <Field.Root flex={1}>
              <Field.Label>Max Completion Tokens</Field.Label>
              <Input
                type="number"
                value={prompt?.max_completion_tokens || ''}
                onChange={(e) => updateField('max_completion_tokens', parseInt(e.target.value))}
                placeholder="e.g., 500"
              />
            </Field.Root>
    
            {/* N Completions */}
            <Field.Root flex={1}>
              <Field.Label>Number of Completions</Field.Label>
              <Input
                type="number"
                value={prompt?.n_completions ?? ''}
                onChange={(e) => updateField('n_completions', parseInt(e.target.value))}
                placeholder="e.g., 1"
                min={1}
              />
            </Field.Root>
            
            {/* Top Logprobs */}
            {prompt?.logprobs && (
              <Field.Root flex={1}>
                <Field.Label>Top Log Probabilities</Field.Label>
                <Input
                  type="number"
                  value={prompt?.top_logprobs ?? ''}
                  onChange={(e) => updateField('top_logprobs', parseInt(e.target.value))}
                  placeholder="e.g., 5"
                  min={0}
                  max={20}
                />
              </Field.Root>
            )}
        </HStack>
        {/* Boolean Switches */}
        <HStack gap={4}>
          <Switch.Root
            checked={prompt.stream ?? false}
            onCheckedChange={(details: { checked: boolean }) => updateField('stream', details.checked)}
          >
            <Switch.HiddenInput />
            <Switch.Control>
              <Switch.Thumb />
            </Switch.Control>
            <Switch.Label>Enable Streaming</Switch.Label>
          </Switch.Root>

          <Switch.Root
            checked={prompt.parallel_tool_calls ?? false}
            onCheckedChange={(details: { checked: boolean }) => updateField('parallel_tool_calls', details.checked)}
          >
            <Switch.HiddenInput />
            <Switch.Control>
              <Switch.Thumb />
            </Switch.Control>
            <Switch.Label>Parallel Tool Calls</Switch.Label>
          </Switch.Root>

          <Switch.Root
            checked={prompt.logprobs ?? false}
            onCheckedChange={(details: { checked: boolean }) => updateField('logprobs', details.checked)}
          >
            <Switch.HiddenInput />
            <Switch.Control>
              <Switch.Thumb />
            </Switch.Control>
            <Switch.Label>Log Probabilities</Switch.Label>
          </Switch.Root>
        </HStack>

      </VStack>
    </Box>
  );
}