'use client';

import React from 'react';
import {
  Box,
  VStack,
  Text,
  Textarea,
} from '@chakra-ui/react';
import { useColorModeValue } from '../../../components/ui/color-mode';
import { extractVariables, hasVariables } from '../_lib/utils/templateUtils';

interface TemplateVariablesProps {
  promptTemplate: string;
  templateVariables: Record<string, string>;
  onUpdateVariable: (variableName: string, value: string) => void;
}

export function TemplateVariables({
  promptTemplate,
  templateVariables,
  onUpdateVariable,
}: TemplateVariablesProps) {
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const bgColor = useColorModeValue('white', 'gray.800');
  const mutedTextColor = useColorModeValue('gray.600', 'gray.400');

  // Extract variables from the prompt template
  const extractedVariables = React.useMemo(() => extractVariables(promptTemplate), [promptTemplate]);

  // Don't render anything if there are no variables
  if (!hasVariables(promptTemplate) || extractedVariables.length === 0) {
    return null;
  }

  return (
    <Box
      p={4}
      borderTopWidth="1px"
      borderColor={borderColor}
      bg={bgColor}
    >
      <VStack gap={3} align="stretch">
        <Text fontSize="sm" fontWeight="medium" color={mutedTextColor}>
          Template Variables - Fill these out before sending your message:
        </Text>
        
        {extractedVariables.map(variable => (
          <Box key={variable}>
            <Text mb={1} fontSize="xs" fontWeight="medium" color={mutedTextColor}>
              {variable}
            </Text>
            <Textarea
              value={templateVariables[variable] || ''}
              onChange={(e) => onUpdateVariable(variable, e.target.value)}
              placeholder={`Enter value for ${variable}...`}
              rows={2}
              fontSize="sm"
              resize="vertical"
              borderColor={borderColor}
            />
          </Box>
        ))}
      </VStack>
    </Box>
  );
}