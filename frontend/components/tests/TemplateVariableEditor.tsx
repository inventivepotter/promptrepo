'use client';

import React from 'react';
import { Box, VStack, HStack, Input, Field, Text, Textarea } from '@chakra-ui/react';

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


  return (
    <Box width="100%">
      <VStack align="stretch" gap={4}>
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
          // Group variables in pairs (2 per row) using full width
          Array.from({ length: Math.ceil(variableEntries.length / 2) }).map((_, rowIndex) => {
            const pairIndex = rowIndex * 2;
            const firstVar = variableEntries[pairIndex];
            const secondVar = variableEntries[pairIndex + 1];
            
            return (
              <HStack key={rowIndex} gap={4} align="start">
                {/* First variable in pair */}
                {firstVar && (
                  <Field.Root flex={1}>
                    <Field.Label fontSize="xs" fontWeight="medium">
                      {firstVar[0]} <Field.RequiredIndicator />
                    </Field.Label>
                    <Textarea
                      value={String(firstVar[1])}
                      onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => handleUpdate(firstVar[0], e.target.value)}
                      placeholder={`Value for ${firstVar[0]}`}
                      rows={2}
                      resize="vertical"
                      size="sm"
                    />
                  </Field.Root>
                )}
                
                {/* Second variable in pair */}
                {secondVar && (
                  <Field.Root flex={1}>
                    <Field.Label fontSize="xs" fontWeight="medium">
                      {secondVar[0]} <Field.RequiredIndicator />
                    </Field.Label>
                    <Textarea
                      value={String(secondVar[1])}
                      onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => handleUpdate(secondVar[0], e.target.value)}
                      placeholder={`Value for ${secondVar[0]}`}
                      rows={2}
                      resize="vertical"
                        size="sm"
                    />
                  </Field.Root>
                )}
                
                {/* Empty placeholder if odd number of variables */}
                {!secondVar && <Box flex={1} />}
              </HStack>
            );
          })
        )}
      </VStack>
    </Box>
  );
}