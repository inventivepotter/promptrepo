'use client';

import React, { useState } from 'react';
import {
  Card,
  VStack,
  HStack,
  Heading,
  Text,
  Badge,
  Collapsible,
  Box,
  Icon,
} from '@chakra-ui/react';
import { FaCheckCircle, FaTimesCircle, FaChevronDown, FaChevronRight } from 'react-icons/fa';
import { TestMetrics } from './TestMetrics';
import type { TestSuiteExecutionResult } from '@/types/test';

interface TestResultsProps {
  execution: TestSuiteExecutionResult;
}

export function TestResults({ execution }: TestResultsProps) {
  const [expandedTests, setExpandedTests] = useState<Set<string>>(new Set());

  const toggleTest = (testName: string) => {
    const newExpanded = new Set(expandedTests);
    if (newExpanded.has(testName)) {
      newExpanded.delete(testName);
    } else {
      newExpanded.add(testName);
    }
    setExpandedTests(newExpanded);
  };

  const overallPassed = execution.failed_tests === 0;

  return (
    <Card.Root>
      <Card.Header>
        <HStack justify="space-between">
          <Heading size="md">Test Results</Heading>
          <HStack gap={2}>
            <Badge colorScheme={overallPassed ? 'green' : 'red'} fontSize="md">
              {overallPassed ? 'PASSED' : 'FAILED'}
            </Badge>
            <Badge variant="outline">
              {execution.passed_tests}/{execution.total_tests} passed
            </Badge>
            <Badge variant="outline">
              {(execution.total_execution_time_ms / 1000).toFixed(2)}s
            </Badge>
          </HStack>
        </HStack>
      </Card.Header>
      <Card.Body>
        <VStack gap={3} align="stretch">
          {execution.test_results.map((testResult) => {
            const isExpanded = expandedTests.has(testResult.test_name);
            
            return (
              <Card.Root
                key={testResult.test_name}
                borderWidth="1px"
                borderColor={testResult.overall_passed ? 'green.500' : 'red.500'}
              >
                <Card.Body>
                  <Collapsible.Root open={isExpanded}>
                    <Collapsible.Trigger
                      onClick={() => toggleTest(testResult.test_name)}
                      width="100%"
                    >
                      <HStack justify="space-between" width="100%">
                        <HStack gap={3}>
                          <Icon
                            as={isExpanded ? FaChevronDown : FaChevronRight}
                            boxSize={4}
                            color="fg.subtle"
                          />
                          <Icon
                            as={testResult.overall_passed ? FaCheckCircle : FaTimesCircle}
                            boxSize={5}
                            color={testResult.overall_passed ? 'green.500' : 'red.500'}
                          />
                          <VStack align="start" gap={0}>
                            <Text fontWeight="semibold">{testResult.test_name}</Text>
                            <Text fontSize="sm" color="fg.subtle">
                              {testResult.prompt_reference}
                            </Text>
                          </VStack>
                        </HStack>
                        <HStack gap={2}>
                          <Badge
                            colorScheme={testResult.overall_passed ? 'green' : 'red'}
                          >
                            {testResult.metric_results.filter(m => m.passed).length}/
                            {testResult.metric_results.length} metrics passed
                          </Badge>
                          <Badge variant="outline">
                            {testResult.execution_time_ms}ms
                          </Badge>
                        </HStack>
                      </HStack>
                    </Collapsible.Trigger>

                    <Collapsible.Content>
                      <VStack gap={4} align="stretch" pt={4} borderTopWidth="1px" mt={4}>
                        {/* Template Variables */}
                        {Object.keys(testResult.template_variables).length > 0 && (
                          <Box>
                            <Text fontSize="sm" fontWeight="semibold" mb={2}>
                              Template Variables
                            </Text>
                            <Box
                              p={3}
                              bg="bg.subtle"
                              borderRadius="md"
                              fontSize="sm"
                              fontFamily="mono"
                            >
                              <pre>{JSON.stringify(testResult.template_variables, null, 2)}</pre>
                            </Box>
                          </Box>
                        )}

                        {/* Actual Output */}
                        <Box>
                          <Text fontSize="sm" fontWeight="semibold" mb={2}>
                            Actual Output
                          </Text>
                          <Box
                            p={3}
                            bg="bg.subtle"
                            borderRadius="md"
                            fontSize="sm"
                            whiteSpace="pre-wrap"
                          >
                            {testResult.actual_output}
                          </Box>
                        </Box>

                        {/* Expected Output */}
                        {testResult.expected_output && (
                          <Box>
                            <Text fontSize="sm" fontWeight="semibold" mb={2}>
                              Expected Output
                            </Text>
                            <Box
                              p={3}
                              bg="bg.subtle"
                              borderRadius="md"
                              fontSize="sm"
                              whiteSpace="pre-wrap"
                            >
                              {testResult.expected_output}
                            </Box>
                          </Box>
                        )}

                        {/* Retrieval Context */}
                        {testResult.retrieval_context && testResult.retrieval_context.length > 0 && (
                          <Box>
                            <Text fontSize="sm" fontWeight="semibold" mb={2}>
                              Retrieval Context
                            </Text>
                            <VStack align="stretch" gap={1}>
                              {testResult.retrieval_context.map((context, idx) => (
                                <Box
                                  key={idx}
                                  p={2}
                                  bg="bg.subtle"
                                  borderRadius="md"
                                  fontSize="sm"
                                >
                                  {context}
                                </Box>
                              ))}
                            </VStack>
                          </Box>
                        )}

                        {/* Metrics */}
                        <TestMetrics results={testResult.metric_results} />

                        {/* Error */}
                        {testResult.error && (
                          <Box>
                            <Text fontSize="sm" fontWeight="semibold" color="red.500" mb={2}>
                              Error
                            </Text>
                            <Box
                              p={3}
                              bg="red.50"
                              borderRadius="md"
                              fontSize="sm"
                              color="red.700"
                            >
                              {testResult.error}
                            </Box>
                          </Box>
                        )}
                      </VStack>
                    </Collapsible.Content>
                  </Collapsible.Root>
                </Card.Body>
              </Card.Root>
            );
          })}
        </VStack>
      </Card.Body>
    </Card.Root>
  );
}