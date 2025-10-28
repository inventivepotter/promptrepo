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
import { ChatMessage } from '../_types/ChatState';
import { MarkdownRenderer } from './MarkdownRenderer';
import { pricingService } from '@/services/llm/pricing/pricingService';

interface ChatMessagesProps {
  messages: ChatMessage[];
  isLoading?: boolean;
}

export function ChatMessages({ messages, isLoading = false }: ChatMessagesProps) {
  const scrollAreaRef = React.useRef<HTMLDivElement>(null);
  
  // Colors
  const mutedTextColor = "fg.muted";
  const timestampColor = "fg.muted";
  
  // AI Message (left side)
  const aiMessageBg = "bg.subtle";
  const aiMessageBorder = "bg.muted";
  
  // User Message (right side - hollow style)
  const userMessageBg = "transparent";
  const userMessageBorder = "bg.muted";
  
  // System Message (right side, muted)
  const systemMessageBg = "bg.subtle";
  const systemMessageBorder = "bg.muted";
  
  // Tool result background
  const toolResultBg = "bg.subtle";

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

  const renderTokenMetrics = (message: ChatMessage) => {
    const usage = message.usage;
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
          {usage.reasoning_tokens && (
            <Text>
              <Text as="span" fontWeight="medium">Reasoning:</Text> {usage.reasoning_tokens}
            </Text>
          )}
          {message.cost && (
            <Text>
              <Text as="span" fontWeight="medium">Cost:</Text> {pricingService.formatCost(message.cost)}
            </Text>
          )}
          {message.model && (
            <Text>
              <Text as="span" fontWeight="medium">Model:</Text> {message.model}
            </Text>
          )}
        </HStack>
      </Box>
    );
  };

  const renderMessage = (message: ChatMessage) => {
    switch (message.role) {
      case 'assistant':
        return (
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
            <Box maxW="85%" flex={1}>
              <Card.Root
                bg={aiMessageBg}
                borderColor={aiMessageBorder}
                borderWidth="1px"
                size="sm"
                opacity={Array.isArray(message.tool_calls) && message.tool_calls.length > 0 ? 0.7 : 1}
              >
                <Card.Body p={3}>
                  {message.content ? (
                    <MarkdownRenderer content={message.content} />
                  ) : Array.isArray(message.tool_calls) && message.tool_calls.length > 0 ? (
                    <Box>
                      <HStack gap={2} mb={2}>
                        <Badge size="xs" variant="subtle" colorPalette="gray">
                          Tool Call
                        </Badge>
                      </HStack>
                      <VStack align="start" gap={2}>
                        {message.tool_calls.map((toolCall) => (
                          <Box key={toolCall.id} w="full">
                            <Text fontSize="sm" color={mutedTextColor}>
                              Name: {toolCall.function.name}
                            </Text>
                            <Text fontSize="sm" color={mutedTextColor} mt={1}>
                              Parameters:
                            </Text>
                            <Box p={2} bg={toolResultBg} borderRadius="md" mt={1}>
                              <Text fontSize="xs" fontFamily="mono" color={mutedTextColor}>
                                {toolCall.function.arguments}
                              </Text>
                            </Box>
                          </Box>
                        ))}
                      </VStack>
                    </Box>
                  ) : (
                    <Text fontSize="sm" color={mutedTextColor} fontStyle="italic">
                      No content
                    </Text>
                  )}
                </Card.Body>
              </Card.Root>
              <Text fontSize="xs" color={timestampColor} mt={1} ml={2}>
                {message.inferenceTimeMs ? formatInferenceTime(message.inferenceTimeMs) : formatTimestamp(message.timestamp)}
              </Text>
              {renderTokenMetrics(message)}
            </Box>
          </HStack>
        );

      case 'user':
        return (
          <HStack align="start" justify="flex-end" w="full" mb={4}>
            <Box maxW="70%" flex={1}>
              <Card.Root
                bg={userMessageBg}
                borderColor={userMessageBorder}
                borderWidth="1px"
                size="sm"
                ml="auto"
                variant="outline"
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
          <HStack align="start" justify="flex-end" w="full" mb={4}>
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
          <HStack align="start" justify="flex-end" w="full" mb={4}>
            <Box maxW="70%" flex={1}>
              <Card.Root
                bg="transparent"
                borderColor={userMessageBorder}
                borderWidth="1px"
                size="sm"
                ml="auto"
                variant="outline"
                opacity={0.7}
              >
                <Card.Body p={3}>
                  <HStack gap={2} mb={2}>
                    <Badge size="xs" variant="subtle" colorPalette="gray">
                      Tool Response
                    </Badge>
                  </HStack>
                  <Text fontSize="sm" whiteSpace="pre-wrap" fontFamily="mono">
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
              opacity={0.7}
            >
              <LuWrench size={16} />
            </Box>
          </HStack>
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
            {messages.map((message) => (
              <React.Fragment key={message.id}>
                {renderMessage(message)}
              </React.Fragment>
            ))}
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
                <Box maxW="85%">
                  <Card.Root
                    bg={aiMessageBg}
                    borderColor={aiMessageBorder}
                    borderWidth="1px"
                    size="sm"
                  >
                    <Card.Body p={3}>
                      <HStack gap={1}>
                        <Box w={2} h={2} bg="primary.solid" borderRadius="full" animation="pulse 1.5s ease-in-out infinite" />
                        <Box w={2} h={2} bg="primary.solid" borderRadius="full" animation="pulse 1.5s ease-in-out infinite" animationDelay="0.2s" />
                        <Box w={2} h={2} bg="primary.solid" borderRadius="full" animation="pulse 1.5s ease-in-out infinite" animationDelay="0.4s" />
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