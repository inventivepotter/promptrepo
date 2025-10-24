'use client';

import {
  Box,
  HStack,
  Text,
  VStack,
  Popover,
} from '@chakra-ui/react';
import { useColorModeValue } from '@/components/ui/color-mode';
import { PiWarning } from 'react-icons/pi';
import { FaInfoCircle } from 'react-icons/fa';
import { useTokenStats, useSessionCost } from '@/stores/chatStore/hooks';
import { pricingService } from '@/services/llm/pricing/pricingService';

export function TokenStats() {
  const { totalInput, totalOutput } = useTokenStats();
  const totalCost = useSessionCost();
  const mutedTextColor = useColorModeValue('gray.600', 'gray.400');
  const accentColor = useColorModeValue('gray.700', 'gray.300');
  const bgColor = useColorModeValue('gray.50', 'gray.700/30');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const linkColor = useColorModeValue('blue.500', 'blue.300');
  const titleColor = useColorModeValue('gray.800', 'gray.200');
  const textColor = useColorModeValue('gray.700', 'gray.300');
  const subTextColor = useColorModeValue('gray.600', 'gray.400');
  
  if (totalInput === 0 && totalOutput === 0) {
    return null;
  }

  return (
    <Box
      px={3}
      py={2}
      bg={bgColor}
      borderBottomWidth="1px"
      borderColor={borderColor}
      fontSize="sm"
    >
      <HStack justify="space-between" align="center">
        <HStack gap={2} align="center">
          <Text fontSize="sm" fontWeight="medium" color={accentColor}>Token Usage</Text>
          <Popover.Root>
            <Popover.Trigger asChild>
              <Box cursor="help" color="gray.500" _hover={{ color: "gray.700" }} _dark={{ color: "gray.400", _hover: { color: "gray.200" } }}>
                <PiWarning size={14} />
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
            <Text as="span" fontWeight="medium">Input:</Text> {totalInput.toLocaleString()}
          </Text>
          <Text>
            <Text as="span" fontWeight="medium">Output:</Text> {totalOutput.toLocaleString()}
          </Text>
          {totalCost > 0 && (
            <Text>
              <Text as="span" fontWeight="medium">Cost:</Text> {pricingService.formatCost(totalCost)}
            </Text>
          )}
        </HStack>
      </HStack>
    </Box>
  );
}