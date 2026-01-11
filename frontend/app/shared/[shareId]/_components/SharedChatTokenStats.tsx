'use client';

import {
  Box,
  HStack,
  Text,
} from '@chakra-ui/react';
import { pricingService } from '@/services/llm/pricing/pricingService';
import type { SharedChatModelConfig } from '@/services/sharedChat';

interface SharedChatTokenStatsProps {
  totalTokens: number;
  totalCost: number;
  modelConfig: SharedChatModelConfig;
}

export function SharedChatTokenStats({
  totalTokens,
  totalCost,
  modelConfig,
}: SharedChatTokenStatsProps) {
  return (
    <Box px={4} py={2} borderBottomWidth="1px" bg="bg.subtle">
      <HStack gap={4} fontSize="xs" color="fg.muted" justify="center" flexWrap="wrap">
        <HStack gap={1}>
          <Text fontWeight="medium">Model:</Text>
          <Text>{modelConfig.provider}/{modelConfig.model}</Text>
        </HStack>
        <Text>|</Text>
        <HStack gap={1}>
          <Text fontWeight="medium">Tokens:</Text>
          <Text>{totalTokens.toLocaleString()}</Text>
        </HStack>
        <Text>|</Text>
        <HStack gap={1}>
          <Text fontWeight="medium">Cost:</Text>
          <Text>{pricingService.formatCost(totalCost)}</Text>
        </HStack>
      </HStack>
    </Box>
  );
}
