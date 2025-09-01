'use client';

import React from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Badge,
  Card,
} from '@chakra-ui/react';
import { LuBot, LuUser, LuSettings, LuWrench } from 'react-icons/lu';
import { useColorModeValue } from '../../../components/ui/color-mode';
import { ChatMessage } from '../_types/ChatState';
import { MarkdownRenderer } from './MarkdownRenderer';

interface ChatMessagesProps {
  messages: ChatMessage[];
  isLoading?: boolean;
}

export function ChatMessages({ messages, isLoading = false }: ChatMessagesProps) {
  const scrollAreaRef = React.useRef<HTMLDivElement>(null);
  
  // Colors
  const mutedTextColor = useColorModeValue('gray.600', 'gray.400');
  const timestampColor = useColorModeValue('gray.500', 'gray.500');
  
  // AI Message (left side)
  const aiMessageBg = useColorModeValue('white', 'gray.800');
  const aiMessageBorder = useColorModeValue('blue.200', 'blue.600');
  
  // User Message (right side)
  const userMessageBg = useColorModeValue('blue.50', 'blue.900');
  const userMessageBorder = useColorModeValue('blue.300', 'blue.500');
  
  // System Message (right side, muted)
  const systemMessageBg = useColorModeValue('gray.50', 'gray.700');
  const systemMessageBorder = useColorModeValue('gray.300', 'gray.500');
  
  // Tool Message (log style)
  const toolMessageBg = useColorModeValue('yellow.50', 'yellow.900');
  const toolMessageBorder = useColorModeValue('yellow.300', 'yellow.600');
  
  // Tool result background
  const toolResultBg = useColorModeValue('gray.50', 'gray.800');

  // Auto scroll to bottom when new messages arrive
  React.useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  const formatTimestamp = (timestamp: Date) => {
    return new Intl.DateTimeFormat('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    }).format(timestamp);
  };

  const formatInferenceTime = (inferenceTimeMs?: number) => {
    if (!inferenceTimeMs) return '';
    
    if (inferenceTimeMs < 1000) {
      return `${Math.round(inferenceTimeMs)}ms`;
    } else {
      return `${(inferenceTimeMs / 1000).toFixed(1)}s`;
    }
  };

  const renderTokenMetrics = (usage?: { prompt_tokens?: number; completion_tokens?: number; total_tokens?: number }) => {
    if (!usage || !usage.total_tokens) return null;
    
    return (
      <Box mt={1} ml={2}>
        <HStack gap={2} fontSize="xs" color={mutedTextColor}>
          <Text>
            <Text as="span" fontWeight="medium">Input:</Text> {usage.prompt_tokens || 0}
          </Text>
          <Text>
            <Text as="span" fontWeight="medium">Output:</Text> {usage.completion_tokens || 0}
          </Text>
        </HStack>
      </Box>
    );
  };

  const renderMessage = (message: ChatMessage) => {
    switch (message.role) {
      case 'assistant':
        return (
          <HStack key={message.id} align="start" justify="flex-start" w="full" mb={4}>
            <Box
              p={2}
              borderRadius="full"
              bg={aiMessageBg}
              borderWidth="1px"
              borderColor={aiMessageBorder}
            >
              <LuBot size={16} />
            </Box>
            <Box maxW="70%" flex={1}>
              <Card.Root
                bg={aiMessageBg}
                borderColor={aiMessageBorder}
                borderWidth="1px"
                size="sm"
              >
                <Card.Body p={3}>
                  <MarkdownRenderer content={message.content} />
                </Card.Body>
              </Card.Root>
              <Text fontSize="xs" color={timestampColor} mt={1} ml={2}>
                {message.inferenceTimeMs ? formatInferenceTime(message.inferenceTimeMs) : formatTimestamp(message.timestamp)}
              </Text>
              {renderTokenMetrics(message.usage)}
            </Box>
          </HStack>
        );

      case 'user':
        return (
          <HStack key={message.id} align="start" justify="flex-end" w="full" mb={4}>
            <Box maxW="70%" flex={1}>
              <Card.Root
                bg={userMessageBg}
                borderColor={userMessageBorder}
                borderWidth="1px"
                size="sm"
                ml="auto"
              >
                <Card.Body p={3}>
                  <Text fontSize="sm" whiteSpace="pre-wrap">
                    {message.content}
                  </Text>
                </Card.Body>
              </Card.Root>
              <Text fontSize="xs" color={timestampColor} mt={1} mr={2} textAlign="right">
                {formatTimestamp(message.timestamp)}
              </Text>
            </Box>
            <Box
              p={2}
              borderRadius="full"
              bg={userMessageBg}
              borderWidth="1px"
              borderColor={userMessageBorder}
            >
              <LuUser size={16} />
            </Box>
          </HStack>
        );

      case 'system':
        return (
          <HStack key={message.id} align="start" justify="flex-end" w="full" mb={4}>
            <Box maxW="70%" flex={1}>
              <Card.Root
                bg={systemMessageBg}
                borderColor={systemMessageBorder}
                borderWidth="1px"
                size="sm"
                ml="auto"
                opacity={0.7}
              >
                <Card.Body p={3}>
                  <HStack gap={2} mb={1}>
                    <Badge size="xs" variant="subtle" colorPalette="gray">
                      System
                    </Badge>
                  </HStack>
                  <Text fontSize="sm" whiteSpace="pre-wrap" color={mutedTextColor}>
                    {message.content}
                  </Text>
                </Card.Body>
              </Card.Root>
              <Text fontSize="xs" color={timestampColor} mt={1} mr={2} textAlign="right">
                {formatTimestamp(message.timestamp)}
              </Text>
            </Box>
            <Box
              p={2}
              borderRadius="full"
              bg={systemMessageBg}
              borderWidth="1px"
              borderColor={systemMessageBorder}
              opacity={0.7}
            >
              <LuSettings size={16} />
            </Box>
          </HStack>
        );

      case 'tool':
        return (
          <Box key={message.id} w="full" mb={3}>
            <Card.Root
              bg={toolMessageBg}
              borderColor={toolMessageBorder}
              borderWidth="1px"
              borderLeftWidth="4px"
              size="sm"
            >
              <Card.Body p={3}>
                <HStack gap={2} mb={2}>
                  <LuWrench size={14} />
                  <Badge size="sm" variant="subtle" colorPalette="yellow">
                    Tool Call
                  </Badge>
                  <Text fontSize="xs" color={timestampColor} ml="auto">
                    {formatTimestamp(message.timestamp)}
                  </Text>
                </HStack>
                <Text fontSize="sm" color={mutedTextColor} whiteSpace="pre-wrap">
                  {message.content}
                </Text>
                {message.tool_calls && (
                  <Box mt={2} p={2} bg={toolResultBg} borderRadius="md">
                    <Text fontSize="xs" color={mutedTextColor}>
                      Tool Calls: {JSON.stringify(message.tool_calls, null, 2)}
                    </Text>
                  </Box>
                )}
              </Card.Body>
            </Card.Root>
          </Box>
        );

      default:
        return null;
    }
  };

  return (
    <Box
      flex={1}
      display="flex"
      flexDirection="column"
      h="full"
      minH={0}
    >
      <Box
        ref={scrollAreaRef}
        flex={1}
        p={4}
        overflowY="auto"
        overflowX="hidden"
        style={{
          scrollBehavior: 'smooth'
        }}
      >
        {messages.length === 0 ? (
          <VStack justify="center" align="center" h="full" color={mutedTextColor}>
            <LuBot size={48} opacity={0.3} />
            <Text fontSize="sm">No messages yet. Start a conversation!</Text>
          </VStack>
        ) : (
          <VStack gap={0} align="stretch">
            {messages.map(renderMessage)}
            {isLoading && (
              <HStack align="start" justify="flex-start" w="full" mb={4}>
                <Box
                  p={2}
                  borderRadius="full"
                  bg={aiMessageBg}
                  borderWidth="1px"
                  borderColor={aiMessageBorder}
                >
                  <LuBot size={16} />
                </Box>
                <Box maxW="70%">
                  <Card.Root
                    bg={aiMessageBg}
                    borderColor={aiMessageBorder}
                    borderWidth="1px"
                    size="sm"
                  >
                    <Card.Body p={3}>
                      <HStack gap={1}>
                        <Box w={2} h={2} bg="blue.400" borderRadius="full" animation="pulse 1.5s ease-in-out infinite" />
                        <Box w={2} h={2} bg="blue.400" borderRadius="full" animation="pulse 1.5s ease-in-out infinite" animationDelay="0.2s" />
                        <Box w={2} h={2} bg="blue.400" borderRadius="full" animation="pulse 1.5s ease-in-out infinite" animationDelay="0.4s" />
                      </HStack>
                    </Card.Body>
                  </Card.Root>
                </Box>
              </HStack>
            )}
          </VStack>
        )}
      </Box>
    </Box>
  );
}