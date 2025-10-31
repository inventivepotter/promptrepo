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
import type { EvalSuiteExecutionResult } from '@/types/eval';

interface EvalResultsProps {
  execution: EvalSuiteExecutionResult;
}

export function EvalResults({ execution }: EvalResultsProps) {
  const [expandedEvals, setExpandedEvals] = useState<Set<string>>(new Set());
  const [isOpen, setIsOpen] = useState(true);

  const toggleEval = (evalName: string) => {
    const newExpanded = new Set(expandedEvals);
    if (newExpanded.has(evalName)) {
      newExpanded.delete(evalName);
    } else {
      newExpanded.add(evalName);
    }
    setExpandedEvals(newExpanded);
  };

  const overallPassed = execution.failed_evals === 0;

  return (
    <Card.Root>
      <Card.Body>
        <Fieldset.Root>
          <HStack justify="space-between" align="center">
            <Stack flex={1}>
              <HStack gap={2}>
                <Fieldset.Legend>Eval Results</Fieldset.Legend>
                <Badge colorScheme={overallPassed ? 'green' : 'red'}>
                  {overallPassed ? 'Passed' : 'Failed'}
                </Badge>
                <Badge variant="outline">
                  {execution.passed_evals}/{execution.total_evals} passed
                </Badge>
                <Badge variant="outline">
                  {(execution.total_execution_time_ms / 1000).toFixed(2)}s
                </Badge>
              </HStack>
              <Fieldset.HelperText color="text.tertiary">
                View detailed results for each eval execution
              </Fieldset.HelperText>
            </Stack>
            <Button
              variant="ghost"
              _hover={{ bg: "bg.subtle" }}
              size="sm"
              onClick={() => setIsOpen(!isOpen)}
              aria-label={isOpen ? "Collapse eval results" : "Expand eval results"}
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
                  {execution.eval_results.map((evalResult) => {
                    const isExpanded = expandedEvals.has(evalResult.eval_name);
                    
                    return (
                      <Card.Root
                        key={evalResult.eval_name}
                        borderWidth="1px"
                        borderColor={evalResult.overall_passed ? 'green.500' : 'red.500'}
                      >
                        <Card.Body>
                          <Collapsible.Root open={isExpanded}>
                            <Collapsible.Trigger
                              onClick={() => toggleEval(evalResult.eval_name)}
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
                                    as={evalResult.overall_passed ? FaCheckCircle : FaTimesCircle}
                                    boxSize={5}
                                    color={evalResult.overall_passed ? 'green.500' : 'red.500'}
                                  />
                                  <VStack align="start" gap={0}>
                                    <Text fontWeight="semibold">{evalResult.eval_name}</Text>
                                    <Text fontSize="sm" color="fg.subtle">
                                      {evalResult.prompt_reference}
                                    </Text>
                                  </VStack>
                                </HStack>
                                <HStack gap={2}>
                                  <Badge
                                    colorScheme={evalResult.overall_passed ? 'green' : 'red'}
                                  >
                                    {(evalResult.metric_results || []).filter(m => m.passed).length}/
                                    {evalResult.metric_results.length} metrics passed
                                  </Badge>
                                  <Badge variant="outline">
                                    {evalResult.actual_evaluation_fields.execution_time_ms}ms
                                  </Badge>
                                </HStack>
                              </HStack>
                            </Collapsible.Trigger>

                            <Collapsible.Content>
                              <VStack gap={4} align="stretch" pt={4} borderTopWidth="1px" mt={4}>
                                {/* Template Variables */}
                                {Object.keys(evalResult.template_variables).length > 0 && (
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
                                      <pre>{JSON.stringify(evalResult.template_variables, null, 2)}</pre>
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
                                    {evalResult.actual_evaluation_fields.actual_output}
                                  </Box>
                                </Box>

                                {/* Expected Output */}
                                {evalResult.expected_evaluation_fields?.config && (
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
                                      <pre>{JSON.stringify(evalResult.expected_evaluation_fields.config, null, 2)}</pre>
                                    </Box>
                                  </Box>
                                )}

                                {/* Tools Called */}
                                {evalResult.actual_evaluation_fields.tools_called && evalResult.actual_evaluation_fields.tools_called.length > 0 && (
                                  <Box>
                                    <Text fontSize="sm" fontWeight="semibold" mb={2}>
                                      Tools Called
                                    </Text>
                                    <VStack align="stretch" gap={1}>
                                      {evalResult.actual_evaluation_fields.tools_called.map((tool: { [key: string]: unknown }, idx: number) => (
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
                                <EvalMetrics results={evalResult.metric_results} />

                                {/* Error */}
                                {evalResult.actual_evaluation_fields.error && (
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
                                      {evalResult.actual_evaluation_fields.error}
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