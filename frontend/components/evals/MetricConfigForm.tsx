'use client';

import React, { useMemo, useState } from 'react';
import { VStack, HStack, Field, Checkbox, Combobox, createListCollection, Box, Input } from '@chakra-ui/react';
import { LuChevronDown, LuInfo } from 'react-icons/lu';
import { Tooltip } from '@/components/ui/tooltip';
import { useConfigStore } from '@/stores/configStore';
import type { MetricConfig } from '@/types/eval';

interface MetricConfigFormProps {
  config: MetricConfig;
  onChange: (config: MetricConfig) => void;
}

export function MetricConfigForm({ config, onChange }: MetricConfigFormProps) {
  const configStore = useConfigStore(state => state.config);
  const [modelSearch, setModelSearch] = useState('');

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseFloat(e.target.value);
    if (!isNaN(value) && value >= 0 && value <= 1) {
      onChange({ ...config, threshold: value });
    }
  };

  // Build provider/model options from config
  const modelOptions = useMemo(() => {
    const llmConfigs = configStore.llm_configs || [];
    return llmConfigs.map(llm => ({
      label: `${llm.provider} / ${llm.model}`,
      value: `${llm.provider}:${llm.model}`,
      provider: llm.provider,
      model: llm.model,
    }));
  }, [configStore.llm_configs]);

  const filteredModels = modelOptions.filter(opt =>
    opt.label.toLowerCase().includes(modelSearch.toLowerCase())
  );

  // Get the display value for the current model
  const currentModelValue = config.model || '';
  const selectedOption = modelOptions.find(opt => opt.value === currentModelValue);
  const displayValue = modelSearch || selectedOption?.label || '';

  return (
    <VStack align="stretch" gap={4}>
      <Field.Root>
        <Field.Label display="flex" alignItems="center" gap={1} fontSize="xs" fontWeight="medium">
          Threshold
          <Tooltip content="Minimum score threshold for this metric (0.0 - 1.0)">
            <Box cursor="help">
              <LuInfo size={12} opacity={0.6} />
            </Box>
          </Tooltip>
        </Field.Label>
        <Input
          type="number"
          value={config.threshold.toFixed(2)}
          onChange={handleInputChange}
          min={0}
          max={1}
          step={0.01}
          size="sm"
          width="120px"
        />
      </Field.Root>

      <Field.Root>
        <Field.Label display="flex" alignItems="center" gap={1} fontSize="xs" fontWeight="medium">
          Evaluation Model
          <Tooltip content="Select the LLM provider and model to use for evaluating this metric">
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
            const newValue = e.value[0] || '';
            onChange({ ...config, model: newValue });
            if (newValue) {
              setModelSearch('');
            }
          }}
          inputValue={displayValue}
          onInputValueChange={(e) => setModelSearch(e.inputValue)}
          openOnClick
        >
          <Combobox.Control position="relative">
            <Combobox.Input
              placeholder="Select evaluation model"
              paddingRight="2rem"
            />
            <Combobox.Trigger position="absolute" right="0.5rem" top="50%" transform="translateY(-50%)">
              <LuChevronDown size={16} />
            </Combobox.Trigger>
          </Combobox.Control>
          <Combobox.Positioner style={{ zIndex: 50 }}>
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
        <Field.HelperText>
          LLM provider and model to use for metric evaluation
        </Field.HelperText>
      </Field.Root>

      <HStack gap={6} align="center">
        <Checkbox.Root
          checked={config.include_reason}
          onCheckedChange={(e) => onChange({ ...config, include_reason: !!e.checked })}
          size="sm"
        >
          <Checkbox.HiddenInput />
          <Checkbox.Control />
          <Checkbox.Label fontSize="xs">Include reasoning in results</Checkbox.Label>
        </Checkbox.Root>

        <Checkbox.Root
          checked={config.strict_mode}
          onCheckedChange={(e) => onChange({ ...config, strict_mode: !!e.checked })}
          size="sm"
        >
          <Checkbox.HiddenInput />
          <Checkbox.Control />
          <Checkbox.Label fontSize="xs">Enable strict evaluation mode</Checkbox.Label>
        </Checkbox.Root>
      </HStack>
    </VStack>
  );
}