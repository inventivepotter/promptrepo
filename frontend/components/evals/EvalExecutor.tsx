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
import type { EvalDefinition } from '@/types/eval';

interface EvalExecutorProps {
  repoName: string;
  suiteName: string;
  evals: EvalDefinition[];
  onExecute: (repoName: string, suiteName: string, evalNames?: string[]) => Promise<void>;
  isExecuting: boolean;
}

export function EvalExecutor({
  repoName,
  suiteName,
  evals,
  onExecute,
  isExecuting,
}: EvalExecutorProps) {
  const [selectedEvals, setSelectedEvals] = useState<Set<string>>(new Set());
  const [isOpen, setIsOpen] = useState(true);

  const enabledEvals = evals.filter(evalItem => evalItem.enabled);
  const allSelected = enabledEvals.length > 0 && selectedEvals.size === enabledEvals.length;

  const handleToggleAll = () => {
    if (allSelected) {
      setSelectedEvals(new Set());
    } else {
      setSelectedEvals(new Set(enabledEvals.map(e => e.name)));
    }
  };

  const handleToggleEval = (evalName: string) => {
    const newSelected = new Set(selectedEvals);
    if (newSelected.has(evalName)) {
      newSelected.delete(evalName);
    } else {
      newSelected.add(evalName);
    }
    setSelectedEvals(newSelected);
  };

  const handleExecute = async () => {
    if (selectedEvals.size > 0) {
      await onExecute(repoName, suiteName, Array.from(selectedEvals));
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
                <Fieldset.Legend>Eval Execution</Fieldset.Legend>
                <Badge colorScheme={isExecuting ? 'yellow' : 'gray'}>
                  {isExecuting ? 'Running...' : 'Ready'}
                </Badge>
              </HStack>
              <Fieldset.HelperText color="text.tertiary">
                Select and execute evals in this suite
              </Fieldset.HelperText>
            </Stack>
            <Button
              variant="ghost"
              _hover={{ bg: "bg.subtle" }}
              size="sm"
              onClick={() => setIsOpen(!isOpen)}
              aria-label={isOpen ? "Collapse eval executor" : "Expand eval executor"}
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
                      disabled={enabledEvals.length === 0 || isExecuting}
                    >
                      <Checkbox.HiddenInput />
                      <Checkbox.Control />
                      <Checkbox.Label>
                        Select All ({selectedEvals.size} of {enabledEvals.length} selected)
                      </Checkbox.Label>
                    </Checkbox.Root>

                    <HStack gap={2}>
                      <Button
                        onClick={handleExecute}
                        colorScheme="green"
                        disabled={enabledEvals.length === 0 || isExecuting}
                        loading={isExecuting}
                      >
                        <FaPlay />
                        {selectedEvals.size > 0
                          ? `Run Selected (${selectedEvals.size})`
                          : 'Run All Evals'}
                      </Button>
                    </HStack>
                  </HStack>

                  {enabledEvals.length === 0 && (
                    <Text fontSize="sm" color="fg.subtle">
                      No enabled tests to execute. Enable at least one test to run the suite.
                    </Text>
                  )}

                  {enabledEvals.length > 0 && (
                    <VStack align="stretch" gap={2} pt={2} borderTopWidth="1px">
                      {enabledEvals.map(evalItem => (
                        <Checkbox.Root
                          key={evalItem.name}
                          checked={selectedEvals.has(evalItem.name)}
                          onCheckedChange={() => handleToggleEval(evalItem.name)}
                          disabled={isExecuting}
                        >
                          <Checkbox.HiddenInput />
                          <Checkbox.Control />
                          <Checkbox.Label>
                            <Text>{evalItem.name}</Text>
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