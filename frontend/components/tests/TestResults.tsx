'use client';

import React, { useState } from 'react';
import {
  Card,
  VStack,
  HStack,
  Text,
  Badge,
  Collapsible,
  Box,
  Icon,
  Fieldset,
  Stack,
  Button,
} from '@chakra-ui/react';
import { FaCheckCircle, FaTimesCircle, FaChevronDown, FaChevronRight } from 'react-icons/fa';
import { LuChevronDown, LuChevronUp } from 'react-icons/lu';
import { TestMetrics } from './TestMetrics';
import type { TestSuiteExecutionResult } from '@/types/test';

interface TestResultsProps {
  execution: TestSuiteExecutionResult;
}

export function TestResults({ execution }: TestResultsProps) {
  const [expandedTests, setExpandedTests] = useState<Set<string>>(new Set());
  const [isOpen, setIsOpen] = useState(true);

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
      <Card.Body>
        <Fieldset.Root>
          <HStack justify="space-between" align="center">
            <Stack flex={1}>
              <HStack gap={2}>
                <Fieldset.Legend>Test Results</Fieldset.Legend>
                <Badge colorScheme={overallPassed ? 'green' : 'red'}>
                  {overallPassed ? 'Passed' : 'Failed'}
                </Badge>
                <Badge variant="outline">
                  {execution.passed_tests}/{execution.total_tests} passed
                </Badge>
                <Badge variant="outline">
                  {(execution.total_execution_time_ms / 1000).toFixed(2)}s
                </Badge>
              </HStack>
              <Fieldset.HelperText color="text.tertiary">
                View detailed results for each test execution
              </Fieldset.HelperText>
            </Stack>
            <Button
              variant="ghost"
              _hover={{ bg: "bg.subtle" }}
              size="sm"
              onClick={() => setIsOpen(!isOpen)}
              aria-label={isOpen ? "Collapse test results" : "Expand test results"}
            >
              <HStack gap={1}>
                <Text fontSize="xs" fontWeight="medium">
                  {isOpen ? "Hide" : "Show"}
                </Text>
                {isOpen ? <LuChevronUp /> : <LuChevronDown />}
              </HStack>
            </Button>
          </HStack>

          <Fieldset.Content>
            <Collapsible.Root open={isOpen}>
              <Collapsible.Content>
                <VStack gap={3} align="stretch" mt={3}>
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
                                    {testResult.actual_evaluation_fields.execution_time_ms}ms
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
                                    {testResult.actual_evaluation_fields.actual_output}
                                  </Box>
                                </Box>

                                {/* Expected Output */}
                                {testResult.expected_evaluation_fields?.config && (
                                  <Box>
                                    <Text fontSize="sm" fontWeight="semibold" mb={2}>
                                      Expected Fields
                                    </Text>
                                    <Box
                                      p={3}
                                      bg="bg.subtle"
                                      borderRadius="md"
                                      fontSize="sm"
                                      fontFamily="mono"
                                    >
                                      <pre>{JSON.stringify(testResult.expected_evaluation_fields.config, null, 2)}</pre>
                                    </Box>
                                  </Box>
                                )}

                                {/* Tools Called */}
                                {testResult.actual_evaluation_fields.tools_called && testResult.actual_evaluation_fields.tools_called.length > 0 && (
                                  <Box>
                                    <Text fontSize="sm" fontWeight="semibold" mb={2}>
                                      Tools Called
                                    </Text>
                                    <VStack align="stretch" gap={1}>
                                      {testResult.actual_evaluation_fields.tools_called.map((tool: { [key: string]: unknown }, idx: number) => (
                                        <Box
                                          key={idx}
                                          p={2}
                                          bg="bg.subtle"
                                          borderRadius="md"
                                          fontSize="sm"
                                          fontFamily="mono"
                                        >
                                          <pre>{JSON.stringify(tool, null, 2)}</pre>
                                        </Box>
                                      ))}
                                    </VStack>
                                  </Box>
                                )}

                                {/* Metrics */}
                                <TestMetrics results={testResult.metric_results} />

                                {/* Error */}
                                {testResult.actual_evaluation_fields.error && (
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
                                      {testResult.actual_evaluation_fields.error}
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
              </Collapsible.Content>
            </Collapsible.Root>
          </Fieldset.Content>
        </Fieldset.Root>
      </Card.Body>
    </Card.Root>
  );
}