'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import {
  Box,
  VStack,
  Text,
  Spinner,
  Container,
} from '@chakra-ui/react';
import { SharedChatApi } from '@/services/sharedChat';
import type { SharedChatResponse } from '@/services/sharedChat';
import { ResponseStatus } from '@/types/OpenApiResponse';
import { SharedChatHeader } from './_components/SharedChatHeader';
import { SharedChatMessages } from './_components/SharedChatMessages';
import { SharedChatTokenStats } from './_components/SharedChatTokenStats';
import { SharedChatFooter } from './_components/SharedChatFooter';

export default function SharedChatPage() {
  const params = useParams();
  const shareId = params.shareId as string;

  const [sharedChat, setSharedChat] = useState<SharedChatResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSharedChat = async () => {
      if (!shareId) return;

      setIsLoading(true);
      setError(null);

      try {
        const response = await SharedChatApi.getSharedChat(shareId);

        if (response.status === ResponseStatus.SUCCESS && response.data) {
          setSharedChat(response.data);
        } else {
          setError('Shared chat not found');
        }
      } catch {
        setError('Failed to load shared chat');
      } finally {
        setIsLoading(false);
      }
    };

    fetchSharedChat();
  }, [shareId]);

  if (isLoading) {
    return (
      <Box minH="100vh" display="flex" alignItems="center" justifyContent="center">
        <VStack gap={4}>
          <Spinner size="lg" />
          <Text color="fg.muted">Loading shared chat...</Text>
        </VStack>
      </Box>
    );
  }

  if (error || !sharedChat) {
    return (
      <Box minH="100vh" display="flex" alignItems="center" justifyContent="center">
        <VStack gap={4}>
          <Text fontSize="xl" fontWeight="semibold">
            {error || 'Chat not found'}
          </Text>
          <Text color="fg.muted">
            This shared chat may have been deleted or the link is invalid.
          </Text>
        </VStack>
      </Box>
    );
  }

  return (
    <Box h="100vh" display="flex" flexDirection="column" bg="bg.canvas" overflow="hidden">
      <Container maxW="4xl" flex={1} display="flex" flexDirection="column" py={4} minH={0}>
        <VStack gap={0} align="stretch" flex={1} bg="bg" borderRadius="lg" overflow="hidden" boxShadow="sm" minH={0}>
          <SharedChatHeader
            title={sharedChat.title}
            createdAt={sharedChat.created_at}
          />
          <SharedChatTokenStats
            totalTokens={sharedChat.total_tokens}
            totalCost={sharedChat.total_cost}
            modelConfig={sharedChat.model_config_data}
          />
          <SharedChatMessages messages={sharedChat.messages} />
          <SharedChatFooter />
        </VStack>
      </Container>
    </Box>
  );
}
