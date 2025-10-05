'use client';

import { useMemo } from 'react';
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
import {
  useCurrentPrompt,
  usePromptActions,
  useUpdateCurrentPromptField,
  usePrimaryModelSearch,
  useFailoverModelSearch,
  useSetPrimaryModelSearch,
  useSetFailoverModelSearch
} from '@/stores/promptStore/hooks';
import { useConfigStore } from '@/stores/configStore';

interface ModelOption {
  label: string;
  value: string;
  provider: string;
  model: string;
}

interface ModelComboboxProps {
  modelOptions: ModelOption[];
  value: string;
  onValueChange: (value: string) => void;
  placeholder: string;
  label: string;
  required?: boolean;
  tooltip: string;
  searchValue: string;
  onSearchChange: (value: string) => void;
}

function ModelCombobox({
  modelOptions,
  value,
  onValueChange,
  placeholder,
  label,
  required,
  tooltip,
  searchValue,
  onSearchChange
}: ModelComboboxProps) {
  const filteredModels = modelOptions.filter(opt =>
    opt.label.toLowerCase().includes(searchValue.toLowerCase())
  );

  // Get the display label for the selected value
  const selectedOption = modelOptions.find(opt => opt.value === value);
  const displayValue = searchValue || selectedOption?.label || '';

  return (
    <Field.Root flex={1} required={required}>
      <Field.Label display="flex" alignItems="center" gap={1} fontSize="xs">
        {label} {required && <Field.RequiredIndicator />}
        {!required && <Field.RequiredIndicator opacity={0.4}>(optional)</Field.RequiredIndicator>}
        <Tooltip content={tooltip}>
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
        value={[value]}
        onValueChange={(e) => {
          const newValue = e.value[0] || '';
          onValueChange(newValue);
          // Clear search when selecting a value
          if (newValue) {
            onSearchChange('');
          }
        }}
        inputValue={displayValue}
        onInputValueChange={(e) => onSearchChange(e.inputValue)}
        openOnClick
      >
        <Combobox.Control position="relative">
          <Combobox.Input
            placeholder={placeholder}
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
  );
}

export function ModelFieldGroup() {
  const currentPrompt = useCurrentPrompt();
  const { setCurrentPrompt } = usePromptActions();
  const updateField = useUpdateCurrentPromptField();
  const config = useConfigStore(state => state.config);
  
  const primaryModelSearch = usePrimaryModelSearch();
  const failoverModelSearch = useFailoverModelSearch();
  const setPrimaryModelSearch = useSetPrimaryModelSearch();
  const setFailoverModelSearch = useSetFailoverModelSearch();

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
            <ModelCombobox
              modelOptions={modelOptions}
              value={currentModelValue}
              onValueChange={(value) => {
                const selected = modelOptions.find(opt => opt.value === value);
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
              placeholder="Select primary model"
              label="Primary Model"
              required
              tooltip="Primary provider and model for generating responses."
              searchValue={primaryModelSearch}
              onSearchChange={setPrimaryModelSearch}
            />

            <ModelCombobox
              modelOptions={modelOptions}
              value={failoverModelValue}
              onValueChange={(value) => {
                setCurrentPrompt({
                  ...currentPrompt,
                  prompt: {
                    ...currentPrompt.prompt,
                    failover_model: value,
                  },
                });
              }}
              placeholder="Select failover model"
              label="Failover Model"
              tooltip="Backup model if primary fails."
              searchValue={failoverModelSearch}
              onSearchChange={setFailoverModelSearch}
            />
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
                <Field.RequiredIndicator opacity={0.4}>(optional)</Field.RequiredIndicator>
                <Tooltip content="Maximum tokens to generate in response. Leave empty for model default.">
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
                allowMouseWheel={false}
              >
                <NumberInput.Input placeholder="Leave empty for default" />
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