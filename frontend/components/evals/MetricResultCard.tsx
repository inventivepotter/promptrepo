'use client';

import React, { useState } from 'react';
import { Card, HStack, VStack, Text, Badge, IconButton, Collapsible, Box } from '@chakra-ui/react';
import { LuChevronDown, LuChevronUp, LuCheck, LuX } from 'react-icons/lu';
import type { MetricResult } from '@/types/eval';

interface MetricResultCardProps {
  result: MetricResult;
}

export function MetricResultCard({ result }: MetricResultCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const getMetricLabel = (type: string): string => {
    return type
      .split('_')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const getScoreColor = (score: number): string => {
    if (score >= 0.8) return 'green';
    if (score >= 0.6) return 'yellow';
    return 'red';
  };

  return (
    <Card.Root>
      <Card.Body>
        <VStack align="stretch" gap={3}>
          <HStack justify="space-between" align="center">
            <HStack gap={2} flex={1}>
              <Text fontWeight="semibold">{getMetricLabel(result.type)}</Text>
              {result.passed ? (
                <Badge variant="solid" colorPalette="green">
                  <HStack gap={1}>
                    <LuCheck size={12} />
                    <span>Passed</span>
                  </HStack>
                </Badge>
              ) : (
                <Badge variant="solid" colorPalette="red">
                  <HStack gap={1}>
                    <LuX size={12} />
                    <span>Failed</span>
                  </HStack>
                </Badge>
              )}
            </HStack>

            {result.reason && (
              <IconButton
                aria-label="Toggle reason"
                size="sm"
                variant="ghost"
                onClick={() => setIsExpanded(!isExpanded)}
              >
                {isExpanded ? <LuChevronUp /> : <LuChevronDown />}
              </IconButton>
            )}
          </HStack>

          <HStack gap={2}>
            <Box flex={1} bg="gray.100" borderRadius="full" h="8px" overflow="hidden">
              <Box
                bg={`${getScoreColor(result.score)}.500`}
                h="100%"
                w={`${result.score * 100}%`}
                transition="width 0.3s"
              />
            </Box>
            <Text fontSize="sm" fontWeight="medium" minW="60px">
              {(result.score * 100).toFixed(0)}%
            </Text>
          </HStack>

          <HStack justify="space-between" fontSize="sm" color="gray.600">
            <Text>Threshold: {(result.threshold * 100).toFixed(0)}%</Text>
            {result.error && (
              <Badge variant="subtle" colorPalette="red">
                Error
              </Badge>
            )}
          </HStack>

          {result.reason && (
            <Collapsible.Root open={isExpanded}>
              <Collapsible.Content>
                <Box
                  mt={2}
                  p={3}
                  bg="gray.50"
                  borderRadius="md"
                  borderLeft="3px solid"
                  borderColor="blue.500"
                >
                  <Text fontSize="sm" fontWeight="medium" mb={1}>
                    Reasoning:
                  </Text>
                  <Text fontSize="sm" color="gray.700">
                    {result.reason}
                  </Text>
                </Box>
              </Collapsible.Content>
            </Collapsible.Root>
          )}

          {result.error && (
            <Box
              p={3}
              bg="red.50"
              borderRadius="md"
              borderLeft="3px solid"
              borderColor="red.500"
            >
              <Text fontSize="sm" fontWeight="medium" mb={1} color="red.700">
                Error:
              </Text>
              <Text fontSize="sm" color="red.600">
                {result.error}
              </Text>
            </Box>
          )}
        </VStack>
      </Card.Body>
    </Card.Root>
  );
}