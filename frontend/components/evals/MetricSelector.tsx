'use client';

import React, { useMemo } from 'react';
import {
  Box,
  VStack,
  HStack,
  Button,
  Text,
  Card,
  IconButton,
  createListCollection,
  Field,
  Combobox,
  Heading,
  Stack,
} from '@chakra-ui/react';
import { LuPlus, LuTrash2, LuChevronDown } from 'react-icons/lu';
import { useMetricsStore } from '@/stores/metricsStore';
import { useConfigStore } from '@/stores/configStore';
import type { MetricConfig, MetricType } from '@/types/eval';

interface MetricSelectorProps {
  metrics: MetricConfig[];
  onChange: (metrics: MetricConfig[]) => void;
}

/**
 * Metric selector component with category grouping and dynamic metadata.
 * Fetches available metrics from the store and groups them by category.
 */
export function MetricSelector({ metrics, onChange }: MetricSelectorProps) {
  const { metadata, isLoading, fetchMetadata, isNonDeterministic } = useMetricsStore();
  const configStore = useConfigStore((state) => state.config);
  const [selectedMetricType, setSelectedMetricType] = React.useState<string>('');
  const [metricSearch, setMetricSearch] = React.useState('');
  const [modelSearches, setModelSearches] = React.useState<Record<number, string>>({});

  // Fetch metadata on mount
  React.useEffect(() => {
    if (!metadata && !isLoading) {
      fetchMetadata();
    }
  }, [metadata, isLoading, fetchMetadata]);

  // Build provider/model options from config
  const modelOptions = useMemo(() => {
    const llmConfigs = configStore.llm_configs || [];
    return llmConfigs.map((llm) => ({
      label: `${llm.provider} / ${llm.model}`,
      value: `${llm.provider}:${llm.model}`,
      provider: llm.provider,
      model: llm.model,
    }));
  }, [configStore.llm_configs]);

  // Build metrics grouped by category
  const groupedMetrics = useMemo(() => {
    if (!metadata) return { deterministic: [], nonDeterministic: [] };

    const deterministic: Array<{ value: string; label: string; description: string }> = [];
    const nonDeterministic: Array<{ value: string; label: string; description: string }> = [];

    Object.entries(metadata).forEach(([type, meta]) => {
      // Format metric type as display name (e.g., "exact_match" -> "Exact Match")
      const displayName = type
        .split('_')
        .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');

      const option = {
        value: type,
        label: displayName,
        description: meta.description,
      };

      if (meta.category === 'deterministic') {
        deterministic.push(option);
      } else {
        nonDeterministic.push(option);
      }
    });

    return { deterministic, nonDeterministic };
  }, [metadata]);

  const allMetricsOptions = useMemo(() => {
    return [...groupedMetrics.deterministic, ...groupedMetrics.nonDeterministic];
  }, [groupedMetrics]);

  const handleAddMetric = () => {
    if (!selectedMetricType || !metadata) return;

    const metricMetadata = metadata[selectedMetricType];
    const isNonDet = metricMetadata.category === 'non_deterministic';

    const newMetric: MetricConfig = {
      type: selectedMetricType as MetricType,
      threshold: 0.7,
      provider: isNonDet ? (modelOptions[0]?.provider || '') : undefined,
      model: isNonDet ? (modelOptions[0]?.model || '') : undefined,
      include_reason: isNonDet,
      strict_mode: false,
    };

    onChange([...metrics, newMetric]);
    setSelectedMetricType('');
  };

  const handleUpdateMetric = (index: number, updates: Partial<MetricConfig>) => {
    const newMetrics = [...metrics];
    newMetrics[index] = { ...newMetrics[index], ...updates };
    onChange(newMetrics);
  };

  const handleRemoveMetric = (index: number) => {
    const newMetrics = metrics.filter((_, i) => i !== index);
    onChange(newMetrics);
  };

  const availableMetrics = useMemo(() => {
    return allMetricsOptions.filter((option) => !metrics.some((m) => m.type === option.value));
  }, [allMetricsOptions, metrics]);

  if (isLoading) {
    return (
      <Box p={4} textAlign="center" color="gray.600" fontSize="sm">
        Loading metrics...
      </Box>
    );
  }

  if (!metadata) {
    return (
      <Box p={4} textAlign="center" color="gray.600" fontSize="sm">
        Failed to load metrics metadata
      </Box>
    );
  }

  return (
    <VStack gap={6} align="stretch">
      {/* Configured Metrics */}
      {metrics.length === 0 ? (
        <Box
          p={4}
          textAlign="center"
          border="1px dashed"
          borderColor="gray.300"
          borderRadius="md"
        >
          <Text fontSize="sm" color="gray.600">
            No metrics configured. Add metrics below to start evaluating.
          </Text>
        </Box>
      ) : (
        <VStack gap={3} align="stretch">
          {metrics.map((metric, index) => {
            const metricMeta = metadata[metric.type];
            const isNonDet = isNonDeterministic(metric.type);
            const currentModelValue = `${metric.provider || ''}:${metric.model || ''}`;
            const selectedOption = modelOptions.find((opt) => opt.value === currentModelValue);
            const modelSearch = modelSearches[index] || '';
            
            // Only show threshold for non-deterministic metrics and fuzzy_match/semantic_similarity
            const shouldShowThreshold = isNonDet ||
              metric.type === 'fuzzy_match' ||
              metric.type === 'semantic_similarity';

            return (
              <Card.Root key={index}>
                <Card.Header>
                  <HStack justify="space-between" align="start">
                    <VStack align="start" gap={1} flex={1}>
                      <Text fontWeight="semibold" fontSize="sm">
                        {metric.type
                          .split('_')
                          .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
                          .join(' ')}
                      </Text>
                      {metricMeta?.description && (
                        <Text fontSize="xs" color="gray.600">
                          {metricMeta.description}
                        </Text>
                      )}
                    </VStack>
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
                  <Stack gap={4}>

                    {/* Threshold - Only for non-deterministic and fuzzy/semantic metrics */}
                    {shouldShowThreshold && (
                      <Field.Root>
                      <Field.Label fontSize="xs" fontWeight="medium">
                        Threshold
                      </Field.Label>
                      <HStack>
                        <input
                          type="number"
                          value={(metric.threshold ?? 0.7).toFixed(2)}
                          onChange={(e) => {
                            const value = parseFloat(e.target.value);
                            if (!isNaN(value) && value >= 0 && value <= 1) {
                              handleUpdateMetric(index, { threshold: value });
                            }
                          }}
                          min={0}
                          max={1}
                          step={0.01}
                          style={{ width: '120px', padding: '4px 8px', borderRadius: '4px', border: '1px solid #ccc' }}
                        />
                      </HStack>
                      <Field.HelperText fontSize="xs">
                        Minimum score threshold (0.0 - 1.0)
                      </Field.HelperText>
                      </Field.Root>
                    )}

                    {/* Provider/Model Selection for Non-Deterministic Metrics */}
                    {isNonDet && (
                      <Field.Root>
                        <Field.Label fontSize="xs" fontWeight="medium">
                          Evaluation Model
                        </Field.Label>
                        <Combobox.Root
                          collection={createListCollection({
                            items: modelOptions.map((opt) => ({
                              value: opt.value,
                              label: opt.label,
                            })),
                          })}
                          value={[currentModelValue]}
                          onValueChange={(e) => {
                            const newValue = e.value[0] || '';
                            const selectedOption = modelOptions.find((opt) => opt.value === newValue);
                            if (selectedOption) {
                              handleUpdateMetric(index, {
                                provider: selectedOption.provider,
                                model: selectedOption.model
                              });
                            } else {
                              handleUpdateMetric(index, {
                                provider: '',
                                model: ''
                              });
                            }
                            if (newValue) {
                              setModelSearches((prev) => ({ ...prev, [index]: '' }));
                            }
                          }}
                          inputValue={modelSearch || selectedOption?.label || ''}
                          onInputValueChange={(e) => setModelSearches((prev) => ({ ...prev, [index]: e.inputValue }))}
                          openOnClick
                          size="sm"
                        >
                          <Combobox.Control position="relative">
                            <Combobox.Input
                              placeholder="Select evaluation model"
                              paddingRight="2rem"
                            />
                            <Combobox.Trigger
                              position="absolute"
                              right="0.5rem"
                              top="50%"
                              transform="translateY(-50%)"
                            >
                              <LuChevronDown size={16} />
                            </Combobox.Trigger>
                          </Combobox.Control>
                          <Combobox.Positioner style={{ zIndex: 50 }}>
                            <Combobox.Content>
                              {modelOptions.map((opt) => (
                                <Combobox.Item key={opt.value} item={opt.value}>
                                  <Combobox.ItemText>{opt.label}</Combobox.ItemText>
                                  <Combobox.ItemIndicator />
                                </Combobox.Item>
                              ))}
                            </Combobox.Content>
                          </Combobox.Positioner>
                        </Combobox.Root>
                        <Field.HelperText fontSize="xs">
                          LLM provider and model for metric evaluation
                        </Field.HelperText>
                      </Field.Root>
                    )}
                  </Stack>
                </Card.Body>
              </Card.Root>
            );
          })}
        </VStack>
      )}

      {/* Add New Metric Section */}
      <Box pt={4} borderTop="1px solid" borderColor="gray.200">
        <VStack align="stretch" gap={4}>
          <Heading size="sm">Add Metric</Heading>

          <Field.Root>
            <Combobox.Root
              collection={createListCollection({
                items: availableMetrics.map((m) => ({
                  value: m.value,
                  label: m.label,
                })),
              })}
              value={selectedMetricType ? [selectedMetricType] : []}
              onValueChange={(e) => {
                const newValue = e.value[0] || '';
                setSelectedMetricType(newValue);
                if (newValue) {
                  setMetricSearch('');
                }
              }}
              inputValue={metricSearch || availableMetrics.find((m) => m.value === selectedMetricType)?.label || ''}
              onInputValueChange={(e) => setMetricSearch(e.inputValue)}
              openOnClick
              size="sm"
              width="full"
              positioning={{ strategy: 'fixed' }}
            >
              <Combobox.Control position="relative">
                <Combobox.Input
                  placeholder="Search and select a metric..."
                  paddingRight="2rem"
                />
                <Combobox.Trigger
                  position="absolute"
                  right="0.5rem"
                  top="50%"
                  transform="translateY(-50%)"
                >
                  <LuChevronDown size={16} />
                </Combobox.Trigger>
              </Combobox.Control>
              <Combobox.Positioner style={{ zIndex: 9999 }}>
                <Combobox.Content maxHeight="400px" overflowY="auto">
                  {/* Deterministic Metrics Group */}
                  {groupedMetrics.deterministic.filter((m) => !metrics.some((metric) => metric.type === m.value)).length > 0 && (
                    <>
                      <Box px={2} py={1} bg="gray.100" borderBottom="1px solid" borderColor="gray.200">
                        <Text fontSize="xs" fontWeight="bold" color="gray.700">
                          Deterministic Metrics
                        </Text>
                      </Box>
                      {groupedMetrics.deterministic
                        .filter((m) => !metrics.some((metric) => metric.type === m.value))
                        .map((option) => (
                          <Combobox.Item key={option.value} item={option.value}>
                            <VStack align="start" gap={0} width="full">
                              <Combobox.ItemText fontWeight="medium" fontSize="sm">
                                {option.label}
                              </Combobox.ItemText>
                              <Text
                                fontSize="xs"
                                color="gray.600"
                                css={{
                                  display: '-webkit-box',
                                  WebkitLineClamp: 2,
                                  WebkitBoxOrient: 'vertical',
                                  overflow: 'hidden',
                                }}
                              >
                                {option.description}
                              </Text>
                            </VStack>
                            <Combobox.ItemIndicator />
                          </Combobox.Item>
                        ))}
                    </>
                  )}

                  {/* Non-Deterministic Metrics Group */}
                  {groupedMetrics.nonDeterministic.filter((m) => !metrics.some((metric) => metric.type === m.value)).length > 0 && (
                    <>
                      <Box px={2} py={1} bg="gray.100" borderBottom="1px solid" borderColor="gray.200" mt={groupedMetrics.deterministic.filter((m) => !metrics.some((metric) => metric.type === m.value)).length > 0 ? 1 : 0}>
                        <Text fontSize="xs" fontWeight="bold" color="gray.700">
                          LLM-based Metrics
                        </Text>
                      </Box>
                      {groupedMetrics.nonDeterministic
                        .filter((m) => !metrics.some((metric) => metric.type === m.value))
                        .map((option) => (
                          <Combobox.Item key={option.value} item={option.value}>
                            <VStack align="start" gap={0} width="full">
                              <Combobox.ItemText fontWeight="medium" fontSize="sm">
                                {option.label}
                              </Combobox.ItemText>
                              <Text
                                fontSize="xs"
                                color="gray.600"
                                css={{
                                  display: '-webkit-box',
                                  WebkitLineClamp: 2,
                                  WebkitBoxOrient: 'vertical',
                                  overflow: 'hidden',
                                }}
                              >
                                {option.description}
                              </Text>
                            </VStack>
                            <Combobox.ItemIndicator />
                          </Combobox.Item>
                        ))}
                    </>
                  )}

                  {availableMetrics.length === 0 && (
                    <Box p={2} textAlign="center">
                      <Text fontSize="xs" color="gray.500">
                        All metrics already configured
                      </Text>
                    </Box>
                  )}
                </Combobox.Content>
              </Combobox.Positioner>
            </Combobox.Root>
            <Field.HelperText fontSize="xs">
              Select a metric to configure for this eval suite
            </Field.HelperText>
          </Field.Root>

          <Button
            onClick={handleAddMetric}
            disabled={!selectedMetricType || availableMetrics.length === 0}
            size="sm"
            width="full"
          >
            <LuPlus /> Add Selected Metric
          </Button>
        </VStack>
      </Box>
    </VStack>
  );
}