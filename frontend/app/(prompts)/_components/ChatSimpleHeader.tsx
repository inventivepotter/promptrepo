'use client';

import {
  HStack,
  VStack,
  Text,
  Button,
  Box,
} from '@chakra-ui/react';
import { LuRefreshCw, LuBot, LuDollarSign } from 'react-icons/lu';
import { useColorModeValue } from '@/components/ui/color-mode';
import { pricingService } from '@/services/llm/pricing/pricingService';
import { useSessionCost } from '@/stores/chatStore/hooks';

interface ChatSimpleHeaderProps {
  onReset: () => void;
  isLoading?: boolean;
}

export function ChatSimpleHeader({
  onReset,
  isLoading = false,
}: ChatSimpleHeaderProps) {
  const mutedTextColor = useColorModeValue('gray.600', 'gray.400');
  const totalCost = useSessionCost();

  return (
    <Box
      p={4}
      borderBottomWidth="1px"
    >
      <VStack gap={3} align="stretch">
        {/* Header with just description and reset button */}
        <HStack justify="space-between" align="center">
          <VStack align="start">
            <HStack>
              <LuBot size={18} />
              <Text fontSize="lg" fontWeight="semibold">
                Agent
              </Text>
              {totalCost > 0 && (
                <HStack gap={1} fontSize="xs" color="green.600" _dark={{ color: "green.400" }}>
                  <LuDollarSign size={12} />
                  <Text fontFamily="mono" fontWeight="medium">
                    {pricingService.formatCost(totalCost)}
                  </Text>
                </HStack>
              )}
            </HStack>
            <Text fontSize="xs" color={mutedTextColor}>
              Your playground to test prompts with AI agents
            </Text>
          </VStack>
          <Button
            size="sm"
            variant="ghost"
            colorPalette="red"
            onClick={onReset}
            disabled={isLoading}
            _hover={{ bg: 'red.50' }}
          >
            <HStack gap={2}>
              <LuRefreshCw size={14} />
              <Text>Reset</Text>
            </HStack>
          </Button>
        </HStack>
      </VStack>
    </Box>
  );
}