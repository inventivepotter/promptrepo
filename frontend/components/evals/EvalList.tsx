'use client';

import React from 'react';
import { Box, VStack, HStack, Text, Badge, IconButton, Card, Checkbox } from '@chakra-ui/react';
import { LuPencil, LuTrash2, LuPlay } from 'react-icons/lu';
import type { EvalDefinition } from '@/types/eval';

interface EvalListProps {
  evals: EvalDefinition[];
  onEdit: (evalName: string) => void;
  onDelete: (evalName: string) => void;
  onRun: (evalName: string) => void;
  onToggleEnabled: (evalName: string, enabled: boolean) => void;
}

export function EvalList({ evals, onEdit, onDelete, onRun, onToggleEnabled }: EvalListProps) {
  if (evals.length === 0) {
    return (
      <Box
        p={8}
        textAlign="center"
        border="1px dashed"
        borderColor="gray.300"
        borderRadius="md"
      >
        <Text fontSize="lg" color="gray.600">
          No evals in this suite
        </Text>
        <Text fontSize="sm" color="gray.500">
          Add an eval to get started
        </Text>
      </Box>
    );
  }

  return (
    <VStack align="stretch" gap={3}>
      {evals.map((evalItem) => (
        <Card.Root key={evalItem.name} opacity={evalItem.enabled ? 1 : 0.6}>
          <Card.Body>
            <HStack justify="space-between" align="start">
              <VStack align="start" gap={2} flex={1}>
                <HStack gap={2}>
                  <Text fontSize="md" fontWeight="semibold">
                    {evalItem.name}
                  </Text>
                  {!evalItem.enabled && (
                    <Badge variant="subtle" colorPalette="gray">
                      Disabled
                    </Badge>
                  )}
                </HStack>
                
                {evalItem.description && (
                  <Text fontSize="sm" color="gray.600">
                    {evalItem.description}
                  </Text>
                )}

                <HStack gap={2} flexWrap="wrap" fontSize="sm">
                  <Badge variant="outline" colorPalette="blue">
                    Prompt: {evalItem.prompt_reference}
                  </Badge>
                  {evalItem.template_variables && Object.keys(evalItem.template_variables).length > 0 && (
                    <Badge variant="outline" colorPalette="green">
                      {Object.keys(evalItem.template_variables || {}).length} variables
                    </Badge>
                  )}
                </HStack>
              </VStack>

              <HStack gap={1}>
                <Checkbox.Root
                  checked={evalItem.enabled}
                  onCheckedChange={(e) => onToggleEnabled(eval.name, !!e.checked)}
                  size="sm"
                >
                  <Checkbox.HiddenInput />
                  <Checkbox.Control />
                </Checkbox.Root>
                <IconButton
                  aria-label="Run eval"
                  size="sm"
                  variant="ghost"
                  colorPalette="green"
                  onClick={() => onRun(eval.name)}
                  disabled={!evalItem.enabled}
                >
                  <LuPlay />
                </IconButton>
                <IconButton
                  aria-label="Edit eval"
                  size="sm"
                  variant="ghost"
                  onClick={() => onEdit(eval.name)}
                >
                  <LuPencil />
                </IconButton>
                <IconButton
                  aria-label="Delete eval"
                  size="sm"
                  variant="ghost"
                  colorPalette="red"
                  onClick={() => onDelete(eval.name)}
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