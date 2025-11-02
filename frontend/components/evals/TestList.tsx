'use client';

import React from 'react';
import { Box, VStack, HStack, Text, Badge, IconButton, Card, Checkbox } from '@chakra-ui/react';
import { LuPencil, LuTrash2, LuPlay } from 'react-icons/lu';
import type { TestDefinition } from '@/types/eval';

interface TestListProps {
  tests: TestDefinition[];
  onEdit: (testName: string) => void;
  onDelete: (testName: string) => void;
  onRun: (testName: string) => void;
  onToggleEnabled: (testName: string, enabled: boolean) => void;
}

export function TestList({ tests, onEdit, onDelete, onRun, onToggleEnabled }: TestListProps) {
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
          No tests in this eval
        </Text>
        <Text fontSize="sm" color="gray.500">
          Add a test to get started
        </Text>
      </Box>
    );
  }

  return (
    <VStack align="stretch" gap={3}>
      {tests.map((testItem) => (
        <Card.Root key={testItem.name} opacity={testItem.enabled ? 1 : 0.6}>
          <Card.Body>
            <HStack justify="space-between" align="start">
              <VStack align="start" gap={2} flex={1}>
                <HStack gap={2}>
                  <Text fontSize="md" fontWeight="semibold">
                    {testItem.name}
                  </Text>
                  {!testItem.enabled && (
                    <Badge variant="subtle" colorPalette="gray">
                      Disabled
                    </Badge>
                  )}
                </HStack>
                
                {testItem.description && (
                  <Text fontSize="sm" color="gray.600">
                    {testItem.description}
                  </Text>
                )}

                <HStack gap={2} flexWrap="wrap" fontSize="sm">
                  <Badge variant="outline" colorPalette="blue">
                    Prompt: {testItem.prompt_reference}
                  </Badge>
                  {testItem.template_variables && Object.keys(testItem.template_variables).length > 0 && (
                    <Badge variant="outline" colorPalette="green">
                      {Object.keys(testItem.template_variables || {}).length} variables
                    </Badge>
                  )}
                </HStack>
              </VStack>

              <HStack gap={1}>
                <Checkbox.Root
                  checked={testItem.enabled}
                  onCheckedChange={(e) => onToggleEnabled(testItem.name, !!e.checked)}
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
                  onClick={() => onRun(testItem.name)}
                  disabled={!testItem.enabled}
                >
                  <LuPlay />
                </IconButton>
                <IconButton
                  aria-label="Edit test"
                  size="sm"
                  variant="ghost"
                  onClick={() => onEdit(testItem.name)}
                >
                  <LuPencil />
                </IconButton>
                <IconButton
                  aria-label="Delete test"
                  size="sm"
                  variant="ghost"
                  colorPalette="red"
                  onClick={() => onDelete(testItem.name)}
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