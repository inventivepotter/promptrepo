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
import { EvalMetrics } from './EvalMetrics';
import type { EvalExecutionResult } from '@/types/eval';

interface EvalResultsProps {
  execution: EvalExecutionResult;
}

export function EvalResults({ execution }: EvalResultsProps) {
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

  // Format execution timestamp
  const formatExecutionTime = (timestamp: string | Date) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;

    return date.toLocaleString();
  };

  return (
    <Box borderWidth="1px" borderRadius="md" p={4} mb={3}>
      <HStack justify="space-between" align="center" mb={3}>
        <HStack gap={2} flex={1}>
          <Badge colorScheme={overallPassed ? 'green' : 'red'} size="sm">
            {overallPassed ? 'Passed' : 'Failed'}
          </Badge>
          <Badge variant="outline" size="sm">
            {execution.passed_tests}/{execution.total_tests} passed
          </Badge>
          <Badge variant="outline" size="sm">
            {(execution.total_execution_time_ms / 1000).toFixed(2)}s
          </Badge>
          {execution.executed_at && (
            <Text fontSize="sm" color="fg.muted">
              • {formatExecutionTime(execution.executed_at)}
            </Text>
          )}
        </HStack>
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

      <Collapsible.Root open={isOpen}>
        <Collapsible.Content>
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
                                    {(testResult.metric_results || []).filter(m => m.passed).length}/
                                    {testResult.metric_results.length} metrics passed
                                  </Badge>
                                  <Badge variant="outline">
                                    {testResult.actual_test_fields.execution_time_ms}ms
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
                                    {testResult.actual_test_fields.actual_output}
                                  </Box>
                                </Box>

                                {/* Expected Output */}
                                {testResult.expected_test_fields?.config && (
                                  <Box>
                                    <Text fontSize="sm" fontWeight="semibold" mb={2}>
                                      {testResult.expected_test_fields.config.expected_output != null &&
                                       Object.keys(testResult.expected_test_fields.config).length === 1
                                        ? 'Expected Output'
                                        : 'Expected Fields'}
                                    </Text>
                                    <Box
                                      p={3}
                                      bg="bg.subtle"
                                      borderRadius="md"
                                      fontSize="sm"
                                      whiteSpace="pre-wrap"
                                    >
                                      {testResult.expected_test_fields.config.expected_output != null &&
                                       Object.keys(testResult.expected_test_fields.config).length === 1 ? (
                                        String(testResult.expected_test_fields.config.expected_output)
                                      ) : (
                                        <pre style={{ fontFamily: 'mono' }}>{JSON.stringify(testResult.expected_test_fields.config, null, 2)}</pre>
                                      )}
                                    </Box>
                                  </Box>
                                )}

                                {/* Tools Called */}
                                {testResult.actual_test_fields.tools_called && testResult.actual_test_fields.tools_called.length > 0 && (
                                  <Box>
                                    <Text fontSize="sm" fontWeight="semibold" mb={2}>
                                      Tools Called
                                    </Text>
                                    <VStack align="stretch" gap={3}>
                                      {(() => {
                                        // Extract tool calls and results
                                        const toolCalls: Array<{ name: string; arguments: Record<string, unknown>; id: string }> = [];
                                        const toolResults: Array<{ content: string; toolCallId: string; toolName: string }> = [];

                                        testResult.actual_test_fields.tools_called.forEach((item: any) => {
                                          if (item.role === 'assistant' && item.tool_calls) {
                                            item.tool_calls.forEach((tc: any) => {
                                              toolCalls.push({
                                                name: tc.name,
                                                arguments: tc.arguments || {},
                                                id: tc.id
                                              });
                                            });
                                          } else if (item.role === 'tool' && item.content) {
                                            toolResults.push({
                                              content: item.content,
                                              toolCallId: item.tool_call_id,
                                              toolName: item.tool_name
                                            });
                                          }
                                        });

                                        return toolCalls.map((toolCall, idx) => {
                                          // Try to match by ID first, then by name and index
                                          let result = toolResults.find(r => r.toolCallId === toolCall.id);
                                          if (!result && toolResults[idx]) {
                                            // Fallback: match by sequential order if IDs don't match
                                            result = toolResults[idx];
                                          }

                                          return (
                                            <Box
                                              key={idx}
                                              p={3}
                                              bg="gray.50"
                                              borderRadius="md"
                                              borderWidth="1px"
                                              borderColor="gray.200"
                                              _dark={{ bg: "gray.800", borderColor: "gray.700" }}
                                            >
                                              <VStack align="stretch" gap={2}>
                                                <HStack gap={2}>
                                                  <Badge colorPalette="purple" size="sm">
                                                    {toolCall.name}
                                                  </Badge>
                                                </HStack>

                                                {Object.keys(toolCall.arguments).length > 0 && (
                                                  <Box>
                                                    <Text fontSize="xs" fontWeight="semibold" color="gray.600" mb={1} _dark={{ color: "gray.400" }}>
                                                      Parameters:
                                                    </Text>
                                                    <Box
                                                      p={2}
                                                      bg="white"
                                                      borderRadius="sm"
                                                      fontSize="xs"
                                                      _dark={{ bg: "gray.900" }}
                                                    >
                                                      {Object.entries(toolCall.arguments).map(([key, value]) => (
                                                        <HStack key={key} gap={1} flexWrap="wrap">
                                                          <Text fontWeight="semibold" color="gray.700" _dark={{ color: "gray.300" }}>{key}:</Text>
                                                          <Text color="gray.600" _dark={{ color: "gray.400" }}>{String(value)}</Text>
                                                        </HStack>
                                                      ))}
                                                    </Box>
                                                  </Box>
                                                )}

                                                {result && (
                                                  <Box>
                                                    <Text fontSize="xs" fontWeight="semibold" color="gray.600" mb={1} _dark={{ color: "gray.400" }}>
                                                      Output:
                                                    </Text>
                                                    <Box
                                                      p={2}
                                                      bg="white"
                                                      borderRadius="sm"
                                                      fontSize="xs"
                                                      whiteSpace="pre-wrap"
                                                      fontFamily="mono"
                                                      color="gray.700"
                                                      _dark={{ bg: "gray.900", color: "gray.300" }}
                                                    >
                                                      {result.content}
                                                    </Box>
                                                  </Box>
                                                )}
                                              </VStack>
                                            </Box>
                                          );
                                        });
                                      })()}
                                    </VStack>
                                  </Box>
                                )}

                                {/* Metrics */}
                                <EvalMetrics results={testResult.metric_results} />

                                {/* Error */}
                                {testResult.actual_test_fields.error && (
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
                                      {testResult.actual_test_fields.error}
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
    </Box>
  );
}