'use client';

import React from 'react';
import { Box, VStack, HStack, Input, Field, IconButton, Text } from '@chakra-ui/react';
import { LuTrash2 } from 'react-icons/lu';

interface TemplateVariableEditorProps {
  variables: Record<string, unknown>;
  onChange: (variables: Record<string, unknown>) => void;
}

export function TemplateVariableEditor({ variables, onChange }: TemplateVariableEditorProps) {
  const variableEntries = Object.entries(variables);

  const handleUpdate = (key: string, value: string) => {
    onChange({
      ...variables,
      [key]: value,
    });
  };

  const handleRemove = (key: string) => {
    const newVariables = { ...variables };
    delete newVariables[key];
    onChange(newVariables);
  };

  return (
    <Box>
      <VStack align="stretch" gap={3}>
        {variableEntries.length === 0 ? (
          <Box
            p={4}
            textAlign="center"
            border="1px dashed"
            borderColor="gray.300"
            borderRadius="md"
          >
            <Text fontSize="sm" color="gray.600">
              Select a prompt to auto-populate template variables
            </Text>
          </Box>
        ) : (
          variableEntries.map(([key, value]) => (
            <HStack key={key} gap={2}>
              <Field.Root flex={1}>
                <Input
                  value={key}
                  disabled
                  placeholder="Variable name"
                  bg="gray.50"
                />
              </Field.Root>
              <Field.Root flex={2}>
                <Input
                  value={String(value)}
                  onChange={(e) => handleUpdate(key, e.target.value)}
                  placeholder="Variable value"
                />
              </Field.Root>
              <IconButton
                aria-label="Remove variable"
                size="sm"
                variant="ghost"
                colorPalette="red"
                onClick={() => handleRemove(key)}
              >
                <LuTrash2 />
              </IconButton>
            </HStack>
          ))
        )}
      </VStack>
    </Box>
  );
}