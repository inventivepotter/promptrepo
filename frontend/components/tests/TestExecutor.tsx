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
import type { UnitTestDefinition } from '@/types/test';

interface TestExecutorProps {
  repoName: string;
  suiteName: string;
  tests: UnitTestDefinition[];
  onExecute: (repoName: string, suiteName: string, testNames?: string[]) => Promise<void>;
  isExecuting: boolean;
}

export function TestExecutor({
  repoName,
  suiteName,
  tests,
  onExecute,
  isExecuting,
}: TestExecutorProps) {
  const [selectedTests, setSelectedTests] = useState<Set<string>>(new Set());
  const [isOpen, setIsOpen] = useState(true);

  const enabledTests = tests.filter(test => test.enabled);
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
      await onExecute(repoName, suiteName, Array.from(selectedTests));
    } else {
      await onExecute(repoName, suiteName);
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
                Select and execute tests in this suite
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
                      No enabled tests to execute. Enable at least one test to run the suite.
                    </Text>
                  )}

                  {enabledTests.length > 0 && (
                    <VStack align="stretch" gap={2} pt={2} borderTopWidth="1px">
                      {enabledTests.map(test => (
                        <Checkbox.Root
                          key={test.name}
                          checked={selectedTests.has(test.name)}
                          onCheckedChange={() => handleToggleTest(test.name)}
                          disabled={isExecuting}
                        >
                          <Checkbox.HiddenInput />
                          <Checkbox.Control />
                          <Checkbox.Label>
                            <Text>{test.name}</Text>
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