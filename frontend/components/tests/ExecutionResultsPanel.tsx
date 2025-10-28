'use client';

import React, { useState } from 'react';
import { Box, VStack, HStack, Text, Badge, Card, Collapsible, IconButton } from '@chakra-ui/react';
import { LuChevronDown, LuChevronUp, LuCheck, LuX, LuClock } from 'react-icons/lu';
import { MetricResultCard } from './MetricResultCard';
import type { TestSuiteExecutionResult, UnitTestExecutionResult } from '@/types/test';

interface ExecutionResultsPanelProps {
  execution: TestSuiteExecutionResult;
}

export function ExecutionResultsPanel({ execution }: ExecutionResultsPanelProps) {
  const [expandedTests, setExpandedTests] = useState<Set<string>>(new Set());

  const toggleTestExpanded = (testName: string) => {
    const newExpanded = new Set(expandedTests);
    if (newExpanded.has(testName)) {
      newExpanded.delete(testName);
    } else {
      newExpanded.add(testName);
    }
    setExpandedTests(newExpanded);
  };

  const formatDuration = (ms: number): string => {
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(2)}s`;
  };

  const formatDate = (dateStr: string): string => {
    const date = new Date(dateStr);
    return date.toLocaleString();
  };

  const passRate = execution.total_tests > 0
    ? (execution.passed_tests / execution.total_tests) * 100
    : 0;

  return (
    <Box>
      <VStack align="stretch" gap={4}>
        {/* Summary Section */}
        <Card.Root>
          <Card.Header>
            <HStack justify="space-between">
              <Text fontSize="lg" fontWeight="bold">
                Execution Summary
              </Text>
              <Badge
                variant="solid"
                colorPalette={execution.passed_tests === execution.total_tests ? 'green' : 'red'}
              >
                {execution.passed_tests === execution.total_tests ? 'All Passed' : 'Some Failed'}
              </Badge>
            </HStack>
          </Card.Header>
          <Card.Body>
            <VStack align="stretch" gap={3}>
              <HStack justify="space-between" flexWrap="wrap" gap={4}>
                <VStack align="start" gap={1}>
                  <Text fontSize="sm" color="gray.600">
                    Total Tests
                  </Text>
                  <Text fontSize="2xl" fontWeight="bold">
                    {execution.total_tests}
                  </Text>
                </VStack>

                <VStack align="start" gap={1}>
                  <Text fontSize="sm" color="gray.600">
                    Passed
                  </Text>
                  <HStack gap={1}>
                    <LuCheck color="green" />
                    <Text fontSize="2xl" fontWeight="bold" color="green.600">
                      {execution.passed_tests}
                    </Text>
                  </HStack>
                </VStack>

                <VStack align="start" gap={1}>
                  <Text fontSize="sm" color="gray.600">
                    Failed
                  </Text>
                  <HStack gap={1}>
                    <LuX color="red" />
                    <Text fontSize="2xl" fontWeight="bold" color="red.600">
                      {execution.failed_tests}
                    </Text>
                  </HStack>
                </VStack>

                <VStack align="start" gap={1}>
                  <Text fontSize="sm" color="gray.600">
                    Pass Rate
                  </Text>
                  <Text fontSize="2xl" fontWeight="bold">
                    {passRate.toFixed(0)}%
                  </Text>
                </VStack>

                <VStack align="start" gap={1}>
                  <Text fontSize="sm" color="gray.600">
                    Duration
                  </Text>
                  <HStack gap={1}>
                    <LuClock />
                    <Text fontSize="2xl" fontWeight="bold">
                      {formatDuration(execution.total_execution_time_ms)}
                    </Text>
                  </HStack>
                </VStack>
              </HStack>

              <Text fontSize="sm" color="gray.600">
                Executed at: {formatDate(execution.executed_at)}
              </Text>
            </VStack>
          </Card.Body>
        </Card.Root>

        {/* Individual Test Results */}
        <Box>
          <Text fontSize="lg" fontWeight="bold" mb={3}>
            Test Results
          </Text>
          <VStack align="stretch" gap={3}>
            {execution.test_results.map((testResult) => (
              <TestResultCard
                key={testResult.test_name}
                result={testResult}
                isExpanded={expandedTests.has(testResult.test_name)}
                onToggle={() => toggleTestExpanded(testResult.test_name)}
              />
            ))}
          </VStack>
        </Box>
      </VStack>
    </Box>
  );
}

// Internal component for individual test result
interface TestResultCardProps {
  result: UnitTestExecutionResult;
  isExpanded: boolean;
  onToggle: () => void;
}

function TestResultCard({ result, isExpanded, onToggle }: TestResultCardProps) {
  const formatDuration = (ms: number): string => {
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(2)}s`;
  };

  return (
    <Card.Root>
      <Card.Body>
        <VStack align="stretch" gap={3}>
          <HStack justify="space-between" cursor="pointer" onClick={onToggle}>
            <HStack gap={2} flex={1}>
              <Text fontWeight="semibold">{result.test_name}</Text>
              {result.overall_passed ? (
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
              <Badge variant="outline">
                {result.metric_results.length} metrics
              </Badge>
            </HStack>

            <HStack gap={2}>
              <Text fontSize="sm" color="gray.600">
                {formatDuration(result.execution_time_ms)}
              </Text>
              <IconButton
                aria-label="Toggle details"
                size="sm"
                variant="ghost"
                onClick={onToggle}
              >
                {isExpanded ? <LuChevronUp /> : <LuChevronDown />}
              </IconButton>
            </HStack>
          </HStack>

          <Collapsible.Root open={isExpanded}>
            <Collapsible.Content>
              <VStack align="stretch" gap={4} pt={2}>
                {result.error && (
                  <Box
                    p={3}
                    bg="red.50"
                    borderRadius="md"
                    borderLeft="3px solid"
                    borderColor="red.500"
                  >
                    <Text fontSize="sm" fontWeight="medium" mb={1} color="red.700">
                      Execution Error:
                    </Text>
                    <Text fontSize="sm" color="red.600">
                      {result.error}
                    </Text>
                  </Box>
                )}

                <Box>
                  <Text fontSize="sm" fontWeight="medium" mb={2}>
                    Prompt: {result.prompt_reference}
                  </Text>
                </Box>

                <Box>
                  <Text fontSize="sm" fontWeight="medium" mb={2}>
                    Actual Output:
                  </Text>
                  <Box
                    p={3}
                    bg="gray.50"
                    borderRadius="md"
                    fontSize="sm"
                    maxH="200px"
                    overflowY="auto"
                  >
                    {result.actual_output}
                  </Box>
                </Box>

                {result.expected_output && (
                  <Box>
                    <Text fontSize="sm" fontWeight="medium" mb={2}>
                      Expected Output:
                    </Text>
                    <Box
                      p={3}
                      bg="gray.50"
                      borderRadius="md"
                      fontSize="sm"
                      maxH="200px"
                      overflowY="auto"
                    >
                      {result.expected_output}
                    </Box>
                  </Box>
                )}

                <Box>
                  <Text fontSize="sm" fontWeight="medium" mb={3}>
                    Metric Results:
                  </Text>
                  <VStack align="stretch" gap={3}>
                    {result.metric_results.map((metricResult, index) => (
                      <MetricResultCard key={index} result={metricResult} />
                    ))}
                  </VStack>
                </Box>
              </VStack>
            </Collapsible.Content>
          </Collapsible.Root>
        </VStack>
      </Card.Body>
    </Card.Root>
  );
}