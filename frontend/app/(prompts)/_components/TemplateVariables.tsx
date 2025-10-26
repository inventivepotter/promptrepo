'use client';

import React from 'react';
import {
  Box,
  VStack,
  Text,
  Textarea,
  HStack,
  Badge,
  Collapsible,
} from '@chakra-ui/react';
import { useColorModeValue } from '@/components/ui/color-mode';
import { LuChevronDown, LuChevronUp } from 'react-icons/lu';
import { TemplateUtils } from '@/services/prompts';

interface TemplateVariablesProps {
  promptTemplate: string;
  templateVariables: Record<string, string>;
  onUpdateVariable: (variableName: string, value: string) => void;
  isExpanded?: boolean;
  onToggle?: () => void;
}

export function TemplateVariables({
  promptTemplate,
  templateVariables,
  onUpdateVariable,
  isExpanded = true,
  onToggle,
}: TemplateVariablesProps) {
  const borderColor = "bg.muted";
  const bgColor = useColorModeValue('white', 'gray.800');
  const mutedTextColor = useColorModeValue('gray.600', 'gray.400');
  const accentColor = useColorModeValue('gray.700', 'gray.300');
  const subtleBgColor = useColorModeValue('gray.50', 'gray.700/30');
  const requiredColor = useColorModeValue('red.500', 'red.400');
  const hoverBgColor = useColorModeValue('gray.100', 'gray.700/50');

  // Extract variables from the prompt template
  const extractedVariables = React.useMemo(() => TemplateUtils.extractVariables(promptTemplate), [promptTemplate]);

  // Don't render anything if there are no variables
  if (!TemplateUtils.hasVariables(promptTemplate) || extractedVariables.length === 0) {
    return null;
  }

  return (
    <Box
      borderTopWidth="1px"
      borderColor={borderColor}
    >
      {/* Collapsible Header - Always visible */}
      <HStack
        px={3}
        py={isExpanded ? 3 : 2}
        justify="space-between"
        align="center"
        cursor={onToggle ? "pointer" : "default"}
        onClick={onToggle}
        bg={subtleBgColor}
        _hover={onToggle ? { bg: hoverBgColor } : {}}
        transition="padding 0.2s, background-color 0.2s"
      >
        <HStack gap={2}>
          <Text fontSize="sm" fontWeight="medium" color={accentColor}>
            Template Variables
          </Text>
          <Badge colorPalette="gray" variant="subtle" size="xs">
            Required
          </Badge>
        </HStack>
        {onToggle && (
          <Box
            as="button"
            aria-label={isExpanded ? "Collapse variables" : "Expand variables"}
            fontSize="2xs"
            color={mutedTextColor}
            _hover={{ color: accentColor }}
            onClick={(e) => {
              e.stopPropagation();
              onToggle();
            }}
            transition="color 0.2s"
          >
            {isExpanded ? <LuChevronUp size={16} /> : <LuChevronDown size={16} />}
          </Box>
        )}
      </HStack>

      {/* Collapsible Content */}
      <Collapsible.Root open={isExpanded}>
        <Collapsible.Content>
          <Box px={4} pb={4} maxHeight="250px" overflow="auto">
            <VStack gap={3} align="stretch">
              <Text fontSize="xs" color={mutedTextColor}>
                Fill all variables before chatting with the agent
              </Text>
              
              {/* Variables */}
              {extractedVariables.map(variable => {
                const isFilled = templateVariables[variable]?.trim();

                return (
                  <Box key={variable}>
                    <HStack mb={1.5} gap={1}>
                      <Text fontSize="xs" fontWeight="medium" color={accentColor}>
                        {variable}
                      </Text>
                      <Text fontSize="xs" color={requiredColor}>
                        *
                      </Text>
                    </HStack>
                    <Textarea
                      value={templateVariables[variable] || ''}
                      onChange={(e) => onUpdateVariable(variable, e.target.value)}
                      placeholder={`Enter ${variable}`}
                      rows={1}
                      fontSize="sm"
                      resize="vertical"
                      borderColor={!isFilled ? requiredColor : borderColor}
                      bg={bgColor}
                      _focus={{
                        borderColor: !isFilled ? requiredColor : 'blue.500',
                        borderWidth: '2px',
                      }}
                      _placeholder={{ color: mutedTextColor }}
                    />
                  </Box>
                );
              })}
            </VStack>
          </Box>
        </Collapsible.Content>
      </Collapsible.Root>
    </Box>
  );
}