'use client';

import { useState } from 'react';
import {
  Box,
  VStack,
  HStack,
  NumberInput,
  Switch,
  Field,
  Button,
  Collapsible,
  Card,
  Text,
  Fieldset,
  Stack,
} from '@chakra-ui/react';
import { Tooltip } from '@/components/ui/tooltip';
import { LuInfo, LuChevronDown, LuChevronUp } from 'react-icons/lu';
import { useCurrentPrompt, useUpdateCurrentPromptField } from '@/stores/promptStore/hooks';

export function ParametersFieldGroup() {
  const currentPrompt = useCurrentPrompt();
  const updateField = useUpdateCurrentPromptField();
  const [showAdvanced, setShowAdvanced] = useState(false);

  if (!currentPrompt) {
    return null;
  }

  const { prompt } = currentPrompt;

  return (
    <Card.Root>
      <Card.Body>
        <Fieldset.Root>
          <HStack justify="space-between" align="center">
            <Stack flex={1}>
              <Fieldset.Legend>Advanced Parameters</Fieldset.Legend>
              <Fieldset.HelperText>
                Fine-tune model behavior with optional advanced settings
              </Fieldset.HelperText>
            </Stack>
            <Button
              variant="ghost"
              _hover={{ bg: "bg.subtle" }}
              size="sm"
              onClick={() => setShowAdvanced(!showAdvanced)}
              aria-label={showAdvanced ? "Collapse advanced parameters" : "Expand advanced parameters"}
            >
              <HStack gap={1}>
                <Text fontSize="xs" fontWeight="medium">
                  {showAdvanced ? "Hide" : "Show"}
                </Text>
                {showAdvanced ? <LuChevronUp /> : <LuChevronDown />}
              </HStack>
            </Button>
          </HStack>

          <Fieldset.Content>
            <Collapsible.Root open={showAdvanced}>
              <Collapsible.Content>
                <VStack gap={3} mt={3} align="stretch">

                  {/* Row 1: All switches horizontally */}
                  <HStack gap={6} align="center" mb={3}>
                    <HStack gap={2} align="center">
                      <Text fontSize="xs" fontWeight="medium">Stream</Text>
                      <Switch.Root
                        checked={prompt.stream ?? false}
                        onCheckedChange={(details: { checked: boolean }) => updateField('stream', details.checked)}
                        size="sm"
                      >
                        <Switch.HiddenInput />
                        <Switch.Control>
                          <Switch.Thumb />
                        </Switch.Control>
                      </Switch.Root>
                    </HStack>

                    <HStack gap={2} align="center">
                      <Text fontSize="xs" fontWeight="medium">Parallel Tool Calls</Text>
                      <Switch.Root
                        checked={prompt.parallel_tool_calls ?? false}
                        onCheckedChange={(details: { checked: boolean }) => updateField('parallel_tool_calls', details.checked)}
                        size="sm"
                      >
                        <Switch.HiddenInput />
                        <Switch.Control>
                          <Switch.Thumb />
                        </Switch.Control>
                      </Switch.Root>
                    </HStack>

                    <HStack gap={2} align="center">
                      <Text fontSize="xs" fontWeight="medium">Log Probabilities</Text>
                      <Switch.Root
                        checked={prompt.logprobs ?? false}
                        onCheckedChange={(details: { checked: boolean }) => updateField('logprobs', details.checked)}
                        size="sm"
                      >
                        <Switch.HiddenInput />
                        <Switch.Control>
                          <Switch.Thumb />
                        </Switch.Control>
                      </Switch.Root>
                    </HStack>
                  </HStack>

                  {/* Row 2: All 4 number inputs */}
                  <HStack gap={4} align="flex-start">
                    <Field.Root flex={1}>
                      <Field.Label fontSize="xs">Presence Penalty</Field.Label>
                      <NumberInput.Root
                        size="sm"
                        inputMode="decimal"
                        onValueChange={(e) => {
                          const value = e.value ? parseFloat(e.value) : null;
                          updateField('presence_penalty', value);
                        }}
                        min={-2}
                        max={2}
                        step={0.1}
                        value={prompt.presence_penalty?.toString() || ''}
                      >
                        <NumberInput.Input placeholder="0.0" />
                        <NumberInput.Control />
                      </NumberInput.Root>
                    </Field.Root>

                    <Field.Root flex={1}>
                      <Field.Label fontSize="xs">Frequency Penalty</Field.Label>
                      <NumberInput.Root
                        size="sm"
                        inputMode="decimal"
                        onValueChange={(e) => {
                          const value = e.value ? parseFloat(e.value) : null;
                          updateField('frequency_penalty', value);
                        }}
                        min={-2}
                        max={2}
                        step={0.1}
                        value={prompt.frequency_penalty?.toString() || ''}
                      >
                        <NumberInput.Input placeholder="0.0" />
                        <NumberInput.Control />
                      </NumberInput.Root>
                    </Field.Root>

                    <Field.Root flex={1}>
                      <Field.Label fontSize="xs">Seed</Field.Label>
                      <NumberInput.Root
                        size="sm"
                        onValueChange={(e) => {
                          const value = e.value ? parseInt(e.value) : null;
                          updateField('seed', value);
                        }}
                        value={prompt.seed?.toString() || ''}
                      >
                        <NumberInput.Input placeholder="12345" />
                        <NumberInput.Control />
                      </NumberInput.Root>
                    </Field.Root>

                    <Field.Root flex={1}>
                      <Field.Label fontSize="xs">Max Completion Tokens</Field.Label>
                      <NumberInput.Root
                        size="sm"
                        onValueChange={(e) => {
                          const value = e.value ? parseInt(e.value) : null;
                          updateField('max_completion_tokens', value);
                        }}
                        min={1}
                        max={100000}
                        value={prompt?.max_completion_tokens?.toString() || ''}
                      >
                        <NumberInput.Input placeholder="500" />
                        <NumberInput.Control />
                      </NumberInput.Root>
                    </Field.Root>
                  </HStack>

                  {/* Row 3: Conditional Top Log Probs input */}
                  {prompt?.logprobs && (
                    <HStack gap={4} align="flex-start">
                      <Field.Root maxW="200px">
                        <Field.Label fontSize="xs">Top Log Probs</Field.Label>
                        <NumberInput.Root
                          size="sm"
                          onValueChange={(e) => {
                            const value = e.value ? parseInt(e.value) : null;
                            updateField('top_logprobs', value);
                          }}
                          min={0}
                          max={20}
                          value={prompt?.top_logprobs?.toString() || ''}
                        >
                          <NumberInput.Input placeholder="5" />
                          <NumberInput.Control />
                        </NumberInput.Root>
                      </Field.Root>
                    </HStack>
                  )}
                </VStack>
              </Collapsible.Content>
            </Collapsible.Root>
          </Fieldset.Content>
        </Fieldset.Root>
      </Card.Body>
    </Card.Root>
  );
}