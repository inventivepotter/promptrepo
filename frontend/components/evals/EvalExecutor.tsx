'use client';

import React, { useState } from 'react';
import {
  Card,
  VStack,
  HStack,
  Button,
  Checkbox,
  Text,
  Badge,
  Collapsible,
  Fieldset,
  Stack,
} from '@chakra-ui/react';
import { FaPlay } from 'react-icons/fa';
import { LuChevronDown, LuChevronUp } from 'react-icons/lu';
import type { TestDefinition } from '@/types/eval';

interface EvalExecutorProps {
  repoName: string;
  filePath: string;
  tests: TestDefinition[];
  onExecute: (repoName: string, filePath: string, testNames?: string[]) => Promise<void>;
  isExecuting: boolean;
}

export function EvalExecutor({
  repoName,
  filePath,
  tests,
  onExecute,
  isExecuting,
}: EvalExecutorProps) {
  const [selectedTests, setSelectedTests] = useState<Set<string>>(new Set());
  const [isOpen, setIsOpen] = useState(true);

  const enabledTests = tests.filter(testItem => testItem.enabled);
  const allSelected = enabledTests.length > 0 && selectedTests.size === enabledTests.length;

  const handleToggleAll = () => {
    if (allSelected) {
      setSelectedTests(new Set());
    } else {
      setSelectedTests(new Set(enabledTests.map(t => t.name)));
    }
  };

  const handleToggleTest = (testName: string) => {
    const newSelected = new Set(selectedTests);
    if (newSelected.has(testName)) {
      newSelected.delete(testName);
    } else {
      newSelected.add(testName);
    }
    setSelectedTests(newSelected);
  };

  const handleExecute = async () => {
    if (selectedTests.size > 0) {
      await onExecute(repoName, filePath, Array.from(selectedTests));
    } else {
      await onExecute(repoName, filePath);
    }
  };

  return (
    <Card.Root>
      <Card.Body>
        <Fieldset.Root>
          <HStack justify="space-between" align="center">
            <Stack flex={1}>
              <HStack gap={2}>
                <Fieldset.Legend>Test Execution</Fieldset.Legend>
                <Badge colorScheme={isExecuting ? 'yellow' : 'gray'}>
                  {isExecuting ? 'Running...' : 'Ready'}
                </Badge>
              </HStack>
              <Fieldset.HelperText color="text.tertiary">
                Select and execute tests in this eval
              </Fieldset.HelperText>
            </Stack>
            <Button
              variant="ghost"
              _hover={{ bg: "bg.subtle" }}
              size="sm"
              onClick={() => setIsOpen(!isOpen)}
              aria-label={isOpen ? "Collapse test executor" : "Expand test executor"}
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
                <VStack gap={4} align="stretch" mt={3}>
                  <HStack justify="space-between">
                    <Checkbox.Root
                      checked={allSelected}
                      onCheckedChange={handleToggleAll}
                      disabled={enabledTests.length === 0 || isExecuting}
                    >
                      <Checkbox.HiddenInput />
                      <Checkbox.Control />
                      <Checkbox.Label>
                        Select All ({selectedTests.size} of {enabledTests.length} selected)
                      </Checkbox.Label>
                    </Checkbox.Root>

                    <HStack gap={2}>
                      <Button
                        onClick={handleExecute}
                        colorScheme="green"
                        disabled={enabledTests.length === 0 || isExecuting}
                        loading={isExecuting}
                      >
                        <FaPlay />
                        {selectedTests.size > 0
                          ? `Run Selected (${selectedTests.size})`
                          : 'Run All Tests'}
                      </Button>
                    </HStack>
                  </HStack>

                  {enabledTests.length === 0 && (
                    <Text fontSize="sm" color="fg.subtle">
                      No enabled tests to execute. Enable at least one test to run the eval.
                    </Text>
                  )}

                  {enabledTests.length > 0 && (
                    <VStack align="stretch" gap={2} pt={2} borderTopWidth="1px">
                      {enabledTests.map(testItem => (
                        <Checkbox.Root
                          key={testItem.name}
                          checked={selectedTests.has(testItem.name)}
                          onCheckedChange={() => handleToggleTest(testItem.name)}
                          disabled={isExecuting}
                        >
                          <Checkbox.HiddenInput />
                          <Checkbox.Control />
                          <Checkbox.Label>
                            <Text>{testItem.name}</Text>
                          </Checkbox.Label>
                        </Checkbox.Root>
                      ))}
                    </VStack>
                  )}
                </VStack>
              </Collapsible.Content>
            </Collapsible.Root>
          </Fieldset.Content>
        </Fieldset.Root>
      </Card.Body>
    </Card.Root>
  );
}