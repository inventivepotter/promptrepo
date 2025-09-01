'use client';

import React from 'react';
import {
  Box,
  HStack,
  Text,
} from '@chakra-ui/react';
import { useColorModeValue } from '@/components/ui/color-mode';

interface TokenStatsProps {
  totalInputTokens: number;
  totalOutputTokens: number;
}

export function TokenStats({ totalInputTokens, totalOutputTokens }: TokenStatsProps) {
  const mutedTextColor = useColorModeValue('gray.600', 'gray.400');
  const bgColor = useColorModeValue('gray.50', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  
  if (totalInputTokens === 0 && totalOutputTokens === 0) {
    return null;
  }

  return (
    <Box
      p={3}
      bg={bgColor}
      borderBottomWidth="1px"
      borderColor={borderColor}
      fontSize="sm"
    >
      <HStack justify="space-between" align="center">
        <Text color={mutedTextColor}>Token Usage</Text>
        <HStack gap={4} color={mutedTextColor}>
          <Text>
            <Text as="span" fontWeight="medium">Input:</Text> {totalInputTokens.toLocaleString()}
          </Text>
          <Text>
            <Text as="span" fontWeight="medium">Output:</Text> {totalOutputTokens.toLocaleString()}
          </Text>
        </HStack>
      </HStack>
    </Box>
  );
}