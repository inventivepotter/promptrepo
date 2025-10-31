'use client';

import React from 'react';
import { Box, VStack, HStack, Text, Badge, Card, Button } from '@chakra-ui/react';
import { LuClock, LuCheck, LuX } from 'react-icons/lu';
import type { EvalSuiteExecutionResult } from '@/types/eval';

interface ExecutionHistoryProps {
  executions: EvalSuiteExecutionResult[];
  onViewExecution: (execution: EvalSuiteExecutionResult) => void;
}

export function ExecutionHistory({ executions, onViewExecution }: ExecutionHistoryProps) {
  const formatDate = (dateStr: string): string => {
    const date = new Date(dateStr);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    
    // Less than 1 minute
    if (diff < 60000) {
      return 'Just now';
    }
    // Less than 1 hour
    if (diff < 3600000) {
      const minutes = Math.floor(diff / 60000);
      return `${minutes} ${minutes === 1 ? 'minute' : 'minutes'} ago`;
    }
    // Less than 1 day
    if (diff < 86400000) {
      const hours = Math.floor(diff / 3600000);
      return `${hours} ${hours === 1 ? 'hour' : 'hours'} ago`;
    }
    // Less than 7 days
    if (diff < 604800000) {
      const days = Math.floor(diff / 86400000);
      return `${days} ${days === 1 ? 'day' : 'days'} ago`;
    }
    
    return date.toLocaleDateString();
  };

  const formatDuration = (ms: number): string => {
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(2)}s`;
  };

  if (executions.length === 0) {
    return (
      <Box
        p={8}
        textAlign="center"
        border="1px dashed"
        borderColor="gray.300"
        borderRadius="md"
      >
        <Text fontSize="lg" color="gray.600">
          No execution history
        </Text>
        <Text fontSize="sm" color="gray.500">
          Run tests to see execution history
        </Text>
      </Box>
    );
  }

  return (
    <Box>
      <VStack align="stretch" gap={3}>
        {executions.map((execution, index) => (
          <Card.Root key={index} cursor="pointer" onClick={() => onViewExecution(execution)}>
            <Card.Body>
              <HStack justify="space-between" align="center">
                <VStack align="start" gap={2} flex={1}>
                  <HStack gap={2}>
                    <Text fontWeight="semibold">
                      {formatDate(execution.executed_at)}
                    </Text>
                    {execution.passed_tests === execution.total_tests ? (
                      <Badge variant="solid" colorPalette="green">
                        <HStack gap={1}>
                          <LuCheck size={12} />
                          <span>All Passed</span>
                        </HStack>
                      </Badge>
                    ) : (
                      <Badge variant="solid" colorPalette="red">
                        <HStack gap={1}>
                          <LuX size={12} />
                          <span>Some Failed</span>
                        </HStack>
                      </Badge>
                    )}
                  </HStack>

                  <HStack gap={4} fontSize="sm" color="gray.600" flexWrap="wrap">
                    <HStack gap={1}>
                      <LuCheck color="green" size={14} />
                      <Text>{execution.passed_tests} passed</Text>
                    </HStack>
                    <HStack gap={1}>
                      <LuX color="red" size={14} />
                      <Text>{execution.failed_tests} failed</Text>
                    </HStack>
                    <HStack gap={1}>
                      <LuClock size={14} />
                      <Text>{formatDuration(execution.total_execution_time_ms)}</Text>
                    </HStack>
                    <Text>•</Text>
                    <Text>{execution.total_tests} total tests</Text>
                  </HStack>
                </VStack>

                <Button
                  variant="ghost"
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation();
                    onViewExecution(execution);
                  }}
                >
                  View Details
                </Button>
              </HStack>
            </Card.Body>
          </Card.Root>
        ))}
      </VStack>
    </Box>
  );
}