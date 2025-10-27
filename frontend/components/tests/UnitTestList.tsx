'use client';

import React from 'react';
import { Box, VStack, HStack, Text, Badge, IconButton, Card, Checkbox } from '@chakra-ui/react';
import { LuPencil, LuTrash2, LuPlay } from 'react-icons/lu';
import type { UnitTestDefinition } from '@/types/test';

interface UnitTestListProps {
  tests: UnitTestDefinition[];
  onEdit: (testName: string) => void;
  onDelete: (testName: string) => void;
  onRun: (testName: string) => void;
  onToggleEnabled: (testName: string, enabled: boolean) => void;
}

export function UnitTestList({ tests, onEdit, onDelete, onRun, onToggleEnabled }: UnitTestListProps) {
  if (tests.length === 0) {
    return (
      <Box
        p={8}
        textAlign="center"
        border="1px dashed"
        borderColor="gray.300"
        borderRadius="md"
      >
        <Text fontSize="lg" color="gray.600">
          No tests in this suite
        </Text>
        <Text fontSize="sm" color="gray.500">
          Add a test to get started
        </Text>
      </Box>
    );
  }

  return (
    <VStack align="stretch" gap={3}>
      {tests.map((test) => (
        <Card.Root key={test.name} opacity={test.enabled ? 1 : 0.6}>
          <Card.Body>
            <HStack justify="space-between" align="start">
              <VStack align="start" gap={2} flex={1}>
                <HStack gap={2}>
                  <Text fontSize="md" fontWeight="semibold">
                    {test.name}
                  </Text>
                  {!test.enabled && (
                    <Badge variant="subtle" colorPalette="gray">
                      Disabled
                    </Badge>
                  )}
                </HStack>
                
                {test.description && (
                  <Text fontSize="sm" color="gray.600">
                    {test.description}
                  </Text>
                )}

                <HStack gap={2} flexWrap="wrap" fontSize="sm">
                  <Badge variant="outline" colorPalette="blue">
                    Prompt: {test.prompt_reference}
                  </Badge>
                  {test.metrics && test.metrics.length > 0 && (
                    <Badge variant="outline" colorPalette="purple">
                      {test.metrics.length} {test.metrics.length === 1 ? 'metric' : 'metrics'}
                    </Badge>
                  )}
                  {Object.keys(test.template_variables).length > 0 && (
                    <Badge variant="outline" colorPalette="green">
                      {Object.keys(test.template_variables).length} variables
                    </Badge>
                  )}
                </HStack>
              </VStack>

              <HStack gap={1}>
                <Checkbox.Root
                  checked={test.enabled}
                  onCheckedChange={(e) => onToggleEnabled(test.name, !!e.checked)}
                  size="sm"
                >
                  <Checkbox.HiddenInput />
                  <Checkbox.Control />
                </Checkbox.Root>
                <IconButton
                  aria-label="Run test"
                  size="sm"
                  variant="ghost"
                  colorPalette="green"
                  onClick={() => onRun(test.name)}
                  disabled={!test.enabled}
                >
                  <LuPlay />
                </IconButton>
                <IconButton
                  aria-label="Edit test"
                  size="sm"
                  variant="ghost"
                  onClick={() => onEdit(test.name)}
                >
                  <LuPencil />
                </IconButton>
                <IconButton
                  aria-label="Delete test"
                  size="sm"
                  variant="ghost"
                  colorPalette="red"
                  onClick={() => onDelete(test.name)}
                >
                  <LuTrash2 />
                </IconButton>
              </HStack>
            </HStack>
          </Card.Body>
        </Card.Root>
      ))}
    </VStack>
  );
}