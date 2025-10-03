'use client';

import {
  Box,
  VStack,
  HStack,
  Text,
  NumberInput,
  Switch,
  Field,
  NativeSelect,
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
        {/* Boolean Switches - First Row */}
        <HStack gap={4} justify="space-between">
          <Box flex={1}>
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
          </Box>

          <Box flex={1}>
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
          </Box>

          <Box flex={1}>
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
          </Box>
        </HStack>

        {/* Reasoning Effort - 1/3 width */}
        <HStack gap={4}>
          <Field.Root width="33%">
            <Field.Label display="flex" alignItems="center" gap={1}>
              Reasoning Effort
              <Tooltip content="Controls the amount of reasoning the model applies. Higher effort levels may improve response quality for complex tasks.">
                <Box cursor="help">
                  <LuInfo size={14} opacity={0.6} />
                </Box>
              </Tooltip>
            </Field.Label>
            <NativeSelect.Root size="sm">
              <NativeSelect.Field
                value={prompt.reasoning_effort || 'auto'}
                onChange={(e) => updateField('reasoning_effort', e.target.value)}
              >
                <option value="auto">Auto</option>
                <option value="minimal">Minimal</option>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </NativeSelect.Field>
              <NativeSelect.Indicator />
            </NativeSelect.Root>
          </Field.Root>
        </HStack>

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
              <Field.Label display="flex" alignItems="center" gap={1}>
                Max Completion Tokens
                <Tooltip content="Maximum number of tokens in the completion output.">
                  <Box cursor="help">
                    <LuInfo size={14} opacity={0.6} />
                  </Box>
                </Tooltip>
              </Field.Label>
              <NumberInput.Root
                size="sm"
                onValueChange={(e) => updateField('max_completion_tokens', parseInt(e.value))}
                min={1}
                max={100000}
                step={1}
                value={prompt?.max_completion_tokens?.toString() || ''}
              >
                <NumberInput.Input placeholder="e.g., 500" />
                <NumberInput.Control />
              </NumberInput.Root>
            </Field.Root>
    
            {/* N Completions */}
            <Field.Root flex={1}>
              <Field.Label display="flex" alignItems="center" gap={1}>
                Number of Completions
                <Tooltip content="How many completion choices to generate for each input.">
                  <Box cursor="help">
                    <LuInfo size={14} opacity={0.6} />
                  </Box>
                </Tooltip>
              </Field.Label>
              <NumberInput.Root
                size="sm"
                onValueChange={(e) => updateField('n_completions', parseInt(e.value))}
                min={1}
                max={10}
                step={1}
                value={prompt?.n_completions?.toString() || ''}
              >
                <NumberInput.Input placeholder="e.g., 1" />
                <NumberInput.Control />
              </NumberInput.Root>
            </Field.Root>
            
            {/* Top Logprobs */}
            {prompt?.logprobs && (
              <Field.Root flex={1}>
                <Field.Label display="flex" alignItems="center" gap={1}>
                  Top Log Probabilities
                  <Tooltip content="Number of most likely tokens to return at each position with log probabilities.">
                    <Box cursor="help">
                      <LuInfo size={14} opacity={0.6} />
                    </Box>
                  </Tooltip>
                </Field.Label>
                <NumberInput.Root
                  size="sm"
                  onValueChange={(e) => updateField('top_logprobs', parseInt(e.value))}
                  min={0}
                  max={20}
                  step={1}
                  value={prompt?.top_logprobs?.toString() || ''}
                >
                  <NumberInput.Input placeholder="e.g., 5" />
                  <NumberInput.Control />
                </NumberInput.Root>
              </Field.Root>
            )}
        </HStack>

      </VStack>
    </Box>
  );
}