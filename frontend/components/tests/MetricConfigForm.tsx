'use client';

import React from 'react';
import { VStack, HStack, Field, Input, Text, Checkbox, Slider } from '@chakra-ui/react';
import type { MetricConfig } from '@/types/test';

interface MetricConfigFormProps {
  config: MetricConfig;
  onChange: (config: MetricConfig) => void;
}

export function MetricConfigForm({ config, onChange }: MetricConfigFormProps) {
  const handleThresholdChange = (details: { value: number[] }) => {
    onChange({ ...config, threshold: details.value[0] });
  };

  return (
    <VStack align="stretch" gap={4}>
      <Field.Root>
        <Field.Label>Threshold</Field.Label>
        <HStack gap={4}>
          <Slider.Root
            value={[config.threshold]}
            onValueChange={handleThresholdChange}
            min={0}
            max={1}
            step={0.05}
            flex={1}
          >
            <Slider.Control>
              <Slider.Track>
                <Slider.Range />
              </Slider.Track>
              <Slider.Thumb index={0} />
            </Slider.Control>
          </Slider.Root>
          <Text minW="50px" fontSize="sm" fontWeight="medium">
            {config.threshold.toFixed(2)}
          </Text>
        </HStack>
        <Field.HelperText>
          Minimum score required to pass (0.0 - 1.0)
        </Field.HelperText>
      </Field.Root>

      <Field.Root>
        <Field.Label>Evaluation Model</Field.Label>
        <Input
          value={config.model}
          onChange={(e) => onChange({ ...config, model: e.target.value })}
          placeholder="gpt-4"
        />
        <Field.HelperText>
          LLM model to use for metric evaluation
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