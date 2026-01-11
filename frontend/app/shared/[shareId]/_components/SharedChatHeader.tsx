'use client';

import {
  Box,
  HStack,
  VStack,
  Text,
} from '@chakra-ui/react';
import { LuBot, LuCalendar } from 'react-icons/lu';
import { Branding } from '@/components/Branding';

interface SharedChatHeaderProps {
  title: string;
  createdAt: string;
}

export function SharedChatHeader({
  title,
  createdAt,
}: SharedChatHeaderProps) {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  };

  return (
    <Box px={4} py={3} borderBottomWidth="1px" bg="bg.subtle">
      <HStack justify="space-between" align="center">
        {/* Left side - Branding */}
        <Branding fontSize="2xl" />

        {/* Right side - Chat title and date */}
        <VStack align="end" gap={0}>
          <HStack gap={2}>
            <LuBot size={16} />
            <Text fontSize="md" fontWeight="semibold">
              {title}
            </Text>
          </HStack>
          <HStack gap={1} color="fg.muted" fontSize="xs">
            <LuCalendar size={10} />
            <Text>{formatDate(createdAt)}</Text>
          </HStack>
        </VStack>
      </HStack>
    </Box>
  );
}
