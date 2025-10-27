'use client';

import React, { useState } from 'react';
import {
  Card,
  VStack,
  HStack,
  Button,
  Heading,
  Checkbox,
  Text,
  Badge,
  Collapsible,
  IconButton,
} from '@chakra-ui/react';
import { FaPlay, FaChevronDown, FaChevronRight } from 'react-icons/fa';
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
      <Collapsible.Root open={isOpen} onOpenChange={(e) => setIsOpen(e.open)}>
        <Card.Header>
          <HStack justify="space-between" width="100%">
            <HStack gap={2}>
              <Heading size="md">Test Execution</Heading>
              <Badge colorScheme={isExecuting ? 'yellow' : 'gray'}>
                {isExecuting ? 'Running...' : 'Ready'}
              </Badge>
            </HStack>
            <Collapsible.Trigger asChild>
              <IconButton
                aria-label="Toggle test executor"
                variant="ghost"
                size="sm"
              >
                {isOpen ? <FaChevronDown /> : <FaChevronRight />}
              </IconButton>
            </Collapsible.Trigger>
          </HStack>
        </Card.Header>
        <Collapsible.Content>
          <Card.Body>
        <VStack gap={4} align="stretch">
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
                    <HStack gap={2}>
                      <Text>{test.name}</Text>
                      {test.metrics && test.metrics.length > 0 && (
                        <Badge variant="outline" size="sm">
                          {test.metrics.length} metrics
                        </Badge>
                      )}
                    </HStack>
                  </Checkbox.Label>
                </Checkbox.Root>
              ))}
            </VStack>
          )}
        </VStack>
          </Card.Body>
        </Collapsible.Content>
      </Collapsible.Root>
    </Card.Root>
  );
}