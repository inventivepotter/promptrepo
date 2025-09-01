'use client';

import React from 'react';
import {
  Box,
  HStack,
  Text,
  VStack,
  Popover,
} from '@chakra-ui/react';
import { useColorModeValue } from '@/components/ui/color-mode';
import { LuInfo } from 'react-icons/lu';
import { FaInfoCircle } from 'react-icons/fa';

interface TokenStatsProps {
  totalInputTokens: number;
  totalOutputTokens: number;
}

export function TokenStats({ totalInputTokens, totalOutputTokens }: TokenStatsProps) {
  const mutedTextColor = useColorModeValue('gray.600', 'gray.400');
  const bgColor = useColorModeValue('gray.50', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const linkColor = useColorModeValue('blue.500', 'blue.300');
  const titleColor = useColorModeValue('gray.800', 'gray.200');
  const textColor = useColorModeValue('gray.700', 'gray.300');
  const subTextColor = useColorModeValue('gray.600', 'gray.400');
  
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
        <HStack gap={2} align="center">
          <Text color={mutedTextColor}>Token Usage</Text>
          <Popover.Root>
            <Popover.Trigger asChild>
              <Box cursor="help" color="gray.500" _hover={{ color: "gray.700" }} _dark={{ color: "gray.400", _hover: { color: "gray.200" } }}>
                <LuInfo size={12} />
              </Box>
            </Popover.Trigger>
            <Popover.Positioner>
              <Popover.Content maxWidth="400px">
                <Popover.Arrow>
                  <Popover.ArrowTip />
                </Popover.Arrow>
                <Popover.Body>
                  <VStack align="start" gap={3} fontSize="sm">
                    <Popover.Title fontWeight="medium" color={titleColor}>
                      Metrics Accuracy Disclaimer
                    </Popover.Title>

                    <Text color={textColor}>
                      The inference time, number of tokens, and cost displayed are realistic estimates but may not be entirely accurate:
                    </Text>
                    
                    <VStack align="start" gap={2} fontSize="sm">
                      <HStack align="start" gap={2}>
                        <FaInfoCircle color={linkColor} size={12} style={{ marginTop: '2px' }} />
                        <Text color={textColor}>
                          <Text as="span" fontWeight="medium">Cost:</Text> May be significantly lower if cache hits occur, as cached responses have reduced pricing
                        </Text>
                      </HStack>
                      <HStack align="start" gap={2}>
                        <FaInfoCircle color={linkColor} size={12} style={{ marginTop: '2px' }} />
                        <Text color={textColor}>
                          <Text as="span" fontWeight="medium">Inference time:</Text> Includes our processing time for API calls, not just model inference
                        </Text>
                      </HStack>
                      <HStack align="start" gap={2}>
                        <FaInfoCircle color={linkColor} size={12} style={{ marginTop: '2px' }} />
                        <Text color={textColor}>
                          <Text as="span" fontWeight="medium">Tokens:</Text> Calculated by word count when providers don&apos;t share exact tokenization data
                        </Text>
                      </HStack>
                    </VStack>

                    <Text fontSize="xs" color={subTextColor}>
                      These metrics provide useful estimates for understanding usage patterns and costs.
                    </Text>
                  </VStack>
                </Popover.Body>
                <Popover.CloseTrigger />
              </Popover.Content>
            </Popover.Positioner>
          </Popover.Root>
        </HStack>
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