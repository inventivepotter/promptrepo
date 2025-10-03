'use client';

import React, { useMemo } from 'react';
import {
  Box,
  HStack,
  VStack,
  Combobox,
  createListCollection,
  Field,
  Card,
  NumberInput,
  NativeSelect,
  Fieldset,
  Stack,
} from '@chakra-ui/react';
import { Tooltip } from '@/components/ui/tooltip';
import { FaChevronDown } from 'react-icons/fa';
import { LuInfo } from 'react-icons/lu';
import { useCurrentPrompt, usePromptActions, useUpdateCurrentPromptField } from '@/stores/promptStore/hooks';
import { useConfigStore } from '@/stores/configStore';

export function ModelFieldGroup() {
  const currentPrompt = useCurrentPrompt();
  const { setCurrentPrompt } = usePromptActions();
  const updateField = useUpdateCurrentPromptField();
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
    <Card.Root>
      <Card.Body>
        <Fieldset.Root>
          <Stack>
            <Fieldset.Legend>Model Configuration</Fieldset.Legend>
            <Fieldset.HelperText>
              Select primary and failover models, and configure generation parameters
            </Fieldset.HelperText>
          </Stack>

          <Fieldset.Content>
            <VStack gap={4} align="stretch">
          <HStack gap={4} align="start">
          {/* Primary Model */}
          <Field.Root flex={1} required>
            <Field.Label display="flex" alignItems="center" gap={1} fontSize="xs">
              Primary Model
              <Tooltip content="Primary provider and model for generating responses.">
                <Box cursor="help">
                  <LuInfo size={12} opacity={0.6} />
                </Box>
              </Tooltip>
            </Field.Label>
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
                  placeholder="Select primary model"
                  paddingRight="2rem"
                />
                <Combobox.Trigger position="absolute" right="0.5rem" top="50%" transform="translateY(-50%)">
                  <FaChevronDown size={14} />
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
          </Field.Root>

          {/* Failover Model */}
          <Field.Root flex={1}>
            <Field.Label display="flex" alignItems="center" gap={1} fontSize="xs">
              Failover Model <Field.RequiredIndicator opacity={0.4}>(optional)</Field.RequiredIndicator>
              <Tooltip content="Backup model if primary fails.">
                <Box cursor="help">
                  <LuInfo size={12} opacity={0.6} />
                </Box>
              </Tooltip>
            </Field.Label>
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
                  placeholder="Select failover model"
                  paddingRight="2rem"
                />
                <Combobox.Trigger position="absolute" right="0.5rem" top="50%" transform="translateY(-50%)">
                  <FaChevronDown size={14} />
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
          </Field.Root>
          </HStack>

          {/* Model Parameters */}
          <HStack gap={4}>
            <Field.Root flex={1}>
              <Field.Label display="flex" alignItems="center" gap={1} fontSize="xs">
                Temperature
                <Tooltip content="Controls randomness. Higher values make output more creative, lower values more focused.">
                  <Box cursor="help">
                    <LuInfo size={12} opacity={0.6} />
                  </Box>
                </Tooltip>
              </Field.Label>
              <NumberInput.Root
                size="sm"
                inputMode="decimal"
                onValueChange={(e) => {
                  const value = e.value ? parseFloat(e.value) : null;
                  updateField('temperature', value);
                }}
                min={0}
                max={2}
                step={0.01}
                value={prompt.temperature?.toString() || ''}
              >
                <NumberInput.Input placeholder="1.0" />
                <NumberInput.Control />
              </NumberInput.Root>
            </Field.Root>

            <Field.Root flex={1}>
              <Field.Label display="flex" alignItems="center" gap={1} fontSize="xs">
                Top P
                <Tooltip content="Probability mass for nucleus sampling.">
                  <Box cursor="help">
                    <LuInfo size={12} opacity={0.6} />
                  </Box>
                </Tooltip>
              </Field.Label>
              <NumberInput.Root
                size="sm"
                inputMode="decimal"
                onValueChange={(e) => {
                  const value = e.value ? parseFloat(e.value) : null;
                  updateField('top_p', value);
                }}
                min={0}
                max={1}
                step={0.01}
                value={prompt.top_p?.toString() || ''}
              >
                <NumberInput.Input placeholder="1.0" />
                <NumberInput.Control />
              </NumberInput.Root>
            </Field.Root>

            <Field.Root flex={1}>
              <Field.Label display="flex" alignItems="center" gap={1} fontSize="xs">
                Max Tokens
                <Tooltip content="Maximum tokens to generate in response.">
                  <Box cursor="help">
                    <LuInfo size={12} opacity={0.6} />
                  </Box>
                </Tooltip>
              </Field.Label>
              <NumberInput.Root
                size="sm"
                onValueChange={(e) => {
                  const value = e.value ? parseInt(e.value) : null;
                  updateField('max_tokens', value);
                }}
                min={1}
                max={100000}
                value={prompt.max_tokens?.toString() || ''}
              >
                <NumberInput.Input placeholder="2048" />
                <NumberInput.Control />
              </NumberInput.Root>
            </Field.Root>

            <Field.Root flex={1}>
              <Field.Label display="flex" alignItems="center" gap={1} fontSize="xs">
                Reasoning Effort
                <Tooltip content="Controls the amount of reasoning the model applies.">
                  <Box cursor="help">
                    <LuInfo size={12} opacity={0.6} />
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
          </VStack>
          </Fieldset.Content>
        </Fieldset.Root>
      </Card.Body>
    </Card.Root>
  );
}