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
import type { MetricResult } from '@/types/test';

interface TestMetricsProps {
  results: MetricResult[];
}

export function TestMetrics({ results }: TestMetricsProps) {
  const [expandedMetrics, setExpandedMetrics] = useState<Set<string>>(new Set());

  const toggleMetric = (metricType: string) => {
    const newExpanded = new Set(expandedMetrics);
    if (newExpanded.has(metricType)) {
      newExpanded.delete(metricType);
    } else {
      newExpanded.add(metricType);
    }
    setExpandedMetrics(newExpanded);
  };

  return (
    <Box>
      <Text fontSize="sm" fontWeight="semibold" mb={2}>
        Metric Results
      </Text>
      <VStack align="stretch" gap={2}>
        {results.map((result) => {
          const isExpanded = expandedMetrics.has(result.type);
          
          return (
            <Box
              key={result.type}
              p={3}
              borderWidth="1px"
              borderRadius="md"
              borderColor={result.passed ? 'green.500' : 'red.500'}
              bg={result.passed ? 'green.50' : 'red.50'}
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
                        {result.type.replace(/_/g, ' ').toUpperCase()}
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