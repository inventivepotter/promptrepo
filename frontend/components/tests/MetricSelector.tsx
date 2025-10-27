'use client';

import React, { useState } from 'react';
import { Box, VStack, HStack, Button, Text, Card, IconButton, Select, Portal, createListCollection } from '@chakra-ui/react';
import { LuPlus, LuTrash2 } from 'react-icons/lu';
import { MetricConfigForm } from './MetricConfigForm';
import { MetricType, type MetricConfig } from '@/types/test';

interface MetricSelectorProps {
  metrics: MetricConfig[];
  onChange: (metrics: MetricConfig[]) => void;
}

const METRIC_OPTIONS = [
  { value: MetricType.ANSWER_RELEVANCY, label: 'Answer Relevancy' },
  { value: MetricType.FAITHFULNESS, label: 'Faithfulness' },
  { value: MetricType.CONTEXTUAL_RELEVANCY, label: 'Contextual Relevancy' },
  { value: MetricType.CONTEXTUAL_PRECISION, label: 'Contextual Precision' },
  { value: MetricType.CONTEXTUAL_RECALL, label: 'Contextual Recall' },
  { value: MetricType.HALLUCINATION, label: 'Hallucination' },
  { value: MetricType.BIAS, label: 'Bias' },
  { value: MetricType.TOXICITY, label: 'Toxicity' },
];

const metricCollection = createListCollection({
  items: METRIC_OPTIONS,
});

export function MetricSelector({ metrics, onChange }: MetricSelectorProps) {
  const [selectedMetricType, setSelectedMetricType] = useState<string>('');

  const handleAddMetric = () => {
    if (!selectedMetricType) return;

    const newMetric: MetricConfig = {
      type: selectedMetricType as MetricType,
      threshold: 0.7,
      model: '', // Will be selected from combobox
      include_reason: true,
      strict_mode: false,
    };

    onChange([...metrics, newMetric]);
    setSelectedMetricType('');
  };

  const handleUpdateMetric = (index: number, updatedMetric: MetricConfig) => {
    const newMetrics = [...metrics];
    newMetrics[index] = updatedMetric;
    onChange(newMetrics);
  };

  const handleRemoveMetric = (index: number) => {
    const newMetrics = metrics.filter((_, i) => i !== index);
    onChange(newMetrics);
  };

  const getMetricLabel = (type: MetricType): string => {
    return METRIC_OPTIONS.find((opt) => opt.value === type)?.label || type;
  };

  const availableMetrics = METRIC_OPTIONS.filter(
    (option) => !metrics.some((m) => m.type === option.value)
  );

  return (
    <Box>
      <VStack align="stretch" gap={4}>
        {metrics.length === 0 ? (
          <Box
            p={4}
            textAlign="center"
            border="1px dashed"
            borderColor="gray.300"
            borderRadius="md"
          >
            <Text fontSize="sm" color="gray.600">
              No metrics configured
            </Text>
          </Box>
        ) : (
          metrics.map((metric, index) => (
            <Card.Root key={index}>
              <Card.Header>
                <HStack justify="space-between">
                  <Text fontWeight="semibold">{getMetricLabel(metric.type)}</Text>
                  <IconButton
                    aria-label="Remove metric"
                    size="sm"
                    variant="ghost"
                    colorPalette="red"
                    onClick={() => handleRemoveMetric(index)}
                  >
                    <LuTrash2 />
                  </IconButton>
                </HStack>
              </Card.Header>
              <Card.Body>
                <MetricConfigForm
                  config={metric}
                  onChange={(updatedMetric) => handleUpdateMetric(index, updatedMetric)}
                />
              </Card.Body>
            </Card.Root>
          ))
        )}

        <Box pt={2} borderTop="1px solid" borderColor="gray.200">
          <Text fontSize="sm" fontWeight="medium" mb={2}>
            Add Metric
          </Text>
          <HStack gap={2}>
            <Select.Root
              collection={metricCollection}
              value={selectedMetricType ? [selectedMetricType] : []}
              onValueChange={(e) => setSelectedMetricType(e.value[0] || '')}
              size="sm"
              flex={1}
            >
              <Select.HiddenSelect />
              <Select.Control>
                <Select.Trigger>
                  <Select.ValueText placeholder="Select metric type" />
                </Select.Trigger>
                <Select.IndicatorGroup>
                  <Select.Indicator />
                </Select.IndicatorGroup>
              </Select.Control>
              <Portal>
                <Select.Positioner style={{ zIndex: 99999 }}>
                  <Select.Content style={{ zIndex: 99999 }}>
                    {availableMetrics.length === 0 ? (
                      <Box p={2} textAlign="center" fontSize="sm" color="gray.600">
                        All metrics have been added
                      </Box>
                    ) : (
                      availableMetrics.map((option) => (
                        <Select.Item key={option.value} item={option.value}>
                          {option.label}
                          <Select.ItemIndicator />
                        </Select.Item>
                      ))
                    )}
                  </Select.Content>
                </Select.Positioner>
              </Portal>
            </Select.Root>
            <Button
              onClick={handleAddMetric}
              disabled={!selectedMetricType || availableMetrics.length === 0}
            >
              <LuPlus /> Add Metric
            </Button>
          </HStack>
        </Box>
      </VStack>
    </Box>
  );
}