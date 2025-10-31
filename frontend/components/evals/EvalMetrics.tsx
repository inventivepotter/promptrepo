'use client';

import React, { useState } from 'react';
import {
  VStack,
  HStack,
  Text,
  Badge,
  Box,
  Collapsible,
  Icon,
} from '@chakra-ui/react';
import { FaCheckCircle, FaTimesCircle, FaChevronDown, FaChevronRight } from 'react-icons/fa';
import { useMetricsStore } from '@/stores/metricsStore';
import type { MetricResult } from '@/types/eval';

interface EvalMetricsProps {
  results: MetricResult[];
  suiteMetrics?: Array<{ type: string; model?: string }>;
}

export function EvalMetrics({ results, suiteMetrics }: EvalMetricsProps) {
  const [expandedMetrics, setExpandedMetrics] = useState<Set<string>>(new Set());
  const { metadata, getMetricMetadata, isNonDeterministic } = useMetricsStore();

  const toggleMetric = (metricType: string) => {
    const newExpanded = new Set(expandedMetrics);
    if (newExpanded.has(metricType)) {
      newExpanded.delete(metricType);
    } else {
      newExpanded.add(metricType);
    }
    setExpandedMetrics(newExpanded);
  };

  // Helper to format metric type as display name
  const formatMetricName = (type: string) => {
    return type
      .split('_')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  return (
    <Box width="100%">
      <Text fontSize="sm" fontWeight="semibold" mb={2}>
        Metric Results
      </Text>
      <VStack align="stretch" gap={2}>
        {results.map((result) => {
          const isExpanded = expandedMetrics.has(result.type);
          const metricMeta = getMetricMetadata(result.type);
          const isNonDet = isNonDeterministic(result.type);
          const suiteMetric = suiteMetrics?.find((m) => m.type === result.type);
          
          return (
            <Box
              key={result.type}
              p={3}
              borderWidth="1px"
              borderRadius="md"
              borderColor={result.passed ? 'green.500' : 'red.500'}
              bg={result.passed ? 'green.50' : 'red.50'}
              width="100%"
            >
              <Collapsible.Root open={isExpanded}>
                <Collapsible.Trigger
                  onClick={() => toggleMetric(result.type)}
                  width="100%"
                >
                  <HStack justify="space-between" width="100%">
                    <HStack gap={2}>
                      <Icon
                        as={isExpanded ? FaChevronDown : FaChevronRight}
                        boxSize={3}
                        color="fg.subtle"
                      />
                      <Icon
                        as={result.passed ? FaCheckCircle : FaTimesCircle}
                        boxSize={4}
                        color={result.passed ? 'green.600' : 'red.600'}
                      />
                      <Text fontSize="sm" fontWeight="medium">
                        {formatMetricName(result.type)}
                      </Text>
                    </HStack>
                    <HStack gap={2}>
                      <Badge
                        colorScheme={result.passed ? 'green' : 'red'}
                        fontSize="xs"
                      >
                        {result.score.toFixed(3)}
                      </Badge>
                      <Text fontSize="xs" color="fg.subtle">
                        threshold: {result.threshold.toFixed(2)}
                      </Text>
                    </HStack>
                  </HStack>
                </Collapsible.Trigger>

                <Collapsible.Content>
                  <VStack align="stretch" gap={2} mt={3} pt={3} borderTopWidth="1px">
                    {/* Metric Description */}
                    {metricMeta?.description && (
                      <Box>
                        <Text fontSize="xs" fontWeight="semibold" mb={1}>
                          Description
                        </Text>
                        <Text fontSize="xs" color="fg.muted">
                          {metricMeta.description}
                        </Text>
                      </Box>
                    )}

                    {/* Provider/Model for non-deterministic metrics */}
                    {isNonDet && suiteMetric?.model && (
                      <Box>
                        <Text fontSize="xs" fontWeight="semibold" mb={1}>
                          Evaluation Model
                        </Text>
                        <Text fontSize="xs" color="fg.muted">
                          {suiteMetric.model.replace(':', ' / ')}
                        </Text>
                      </Box>
                    )}
                    
                    {result.reason && (
                      <Box>
                        <Text fontSize="xs" fontWeight="semibold" mb={1}>
                          Reasoning
                        </Text>
                        <Text fontSize="xs" color="fg.muted" whiteSpace="pre-wrap">
                          {result.reason}
                        </Text>
                      </Box>
                    )}
                    
                    {result.error && (
                      <Box>
                        <Text fontSize="xs" fontWeight="semibold" color="red.600" mb={1}>
                          Error
                        </Text>
                        <Text fontSize="xs" color="red.600">
                          {result.error}
                        </Text>
                      </Box>
                    )}

                    <HStack justify="space-between" fontSize="xs" color="fg.subtle">
                      <Text>Score: {result.score.toFixed(3)}</Text>
                      <Text>Threshold: {result.threshold.toFixed(2)}</Text>
                      <Text>
                        Status: {result.passed ? 'PASSED' : 'FAILED'}
                      </Text>
                    </HStack>
                  </VStack>
                </Collapsible.Content>
              </Collapsible.Root>
            </Box>
          );
        })}
      </VStack>
    </Box>
  );
}