'use client';

import React, { useMemo, useState } from 'react';
import { VStack, HStack, Field, Checkbox, Slider, Combobox, createListCollection, Box, Input } from '@chakra-ui/react';
import { LuChevronDown, LuInfo } from 'react-icons/lu';
import { Tooltip } from '@/components/ui/tooltip';
import { useConfigStore } from '@/stores/configStore';
import type { MetricConfig } from '@/types/test';

interface MetricConfigFormProps {
  config: MetricConfig;
  onChange: (config: MetricConfig) => void;
}

interface ModelOption {
  label: string;
  value: string;
  provider: string;
  model: string;
}

export function MetricConfigForm({ config, onChange }: MetricConfigFormProps) {
  const configStore = useConfigStore(state => state.config);
  const [modelSearch, setModelSearch] = useState('');

  const handleThresholdChange = (details: { value: number[] }) => {
    onChange({ ...config, threshold: details.value[0] });
  };

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
        <HStack justify="space-between" align="center" mb={2}>
          <Field.Label mb={0}>Threshold</Field.Label>
          <Input
            type="number"
            value={config.threshold.toFixed(2)}
            onChange={handleInputChange}
            min={0}
            max={1}
            step={0.01}
            size="sm"
            width="80px"
          />
        </HStack>
        <Slider.Root
          width="40%"
          value={[config.threshold]}
          onValueChange={handleThresholdChange}
          min={0}
          max={1}
          step={0.01}
          colorPalette="blue"
        >
          <Slider.Control>
            <Slider.Track bg="gray.400" borderWidth="1px" borderColor="gray.300">
              <Slider.Range bg="colorPalette.500" />
            </Slider.Track>
            <Slider.Thumb index={0}>
              <Slider.HiddenInput />
            </Slider.Thumb>
          </Slider.Control>
        </Slider.Root>
      </Field.Root>

      <Field.Root>
        <Field.Label display="flex" alignItems="center" gap={1}>
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

      <VStack align="stretch" gap={2}>
        <Checkbox.Root
          checked={config.include_reason}
          onCheckedChange={(e) => onChange({ ...config, include_reason: !!e.checked })}
        >
          <Checkbox.HiddenInput />
          <Checkbox.Control />
          <Checkbox.Label>Include reasoning in results</Checkbox.Label>
        </Checkbox.Root>

        <Checkbox.Root
          checked={config.strict_mode}
          onCheckedChange={(e) => onChange({ ...config, strict_mode: !!e.checked })}
        >
          <Checkbox.HiddenInput />
          <Checkbox.Control />
          <Checkbox.Label>Enable strict evaluation mode</Checkbox.Label>
        </Checkbox.Root>
      </VStack>
    </VStack>
  );
}