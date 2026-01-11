'use client';

import React, { useState } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Badge,
  Card,
} from '@chakra-ui/react';
import { LuBot, LuUser, LuSettings, LuWrench, LuChevronDown, LuChevronUp } from 'react-icons/lu';
import type { SharedChatMessage } from '@/services/sharedChat';
import { pricingService } from '@/services/llm/pricing/pricingService';

interface SharedChatMessagesProps {
  messages: SharedChatMessage[];
}

// Collapsible System Message Component
function CollapsibleSystemMessage({
  content,
  timestamp,
  formatTimestamp,
}: {
  content: string;
  timestamp: string;
  formatTimestamp: (ts: string) => string;
}) {
  const [isExpanded, setIsExpanded] = useState(false);
  const lines = content.split('\n');
  const maxLines = 4;
  const needsCollapse = lines.length > maxLines;

  const displayContent = needsCollapse && !isExpanded
    ? lines.slice(0, maxLines).join('\n') + '...'
    : content;

  const mutedTextColor = 'fg.muted';
  const timestampColor = 'fg.muted';
  const systemMessageBg = 'bg.subtle';
  const systemMessageBorder = 'bg.muted';

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
          cursor={needsCollapse ? 'pointer' : 'default'}
          onClick={() => needsCollapse && setIsExpanded(!isExpanded)}
          _hover={needsCollapse ? { opacity: 0.8 } : undefined}
          transition="opacity 0.2s"
        >
          <Card.Body p={3}>
            <HStack gap={2} mb={1} justify="space-between">
              <Badge size="xs" variant="subtle" colorPalette="gray">
                System Prompt
              </Badge>
              {needsCollapse && (
                <HStack gap={1} fontSize="xs" color={mutedTextColor}>
                  <Text>{isExpanded ? 'Show less' : 'Show more'}</Text>
                  {isExpanded ? <LuChevronUp size={12} /> : <LuChevronDown size={12} />}
                </HStack>
              )}
            </HStack>
            <Text
              fontSize="sm"
              whiteSpace="pre-wrap"
              color={mutedTextColor}
              overflow="hidden"
            >
              {displayContent}
            </Text>
          </Card.Body>
        </Card.Root>
        <Text
          fontSize="xs"
          color={timestampColor}
          mt={1}
          mr={2}
          textAlign="right"
        >
          {formatTimestamp(timestamp)}
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
}

export function SharedChatMessages({ messages }: SharedChatMessagesProps) {
  const scrollAreaRef = React.useRef<HTMLDivElement>(null);

  // Colors
  const mutedTextColor = 'fg.muted';
  const timestampColor = 'fg.muted';

  // AI Message (left side)
  const aiMessageBg = 'bg.subtle';
  const aiMessageBorder = 'bg.muted';

  // User Message (right side - hollow style)
  const userMessageBg = 'transparent';
  const userMessageBorder = 'bg.muted';

  // Tool result background
  const toolResultBg = 'bg.subtle';

  const formatTimestamp = (timestampStr: string) => {
    const timestamp = new Date(timestampStr);
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

  const renderTokenMetrics = (message: SharedChatMessage) => {
    const usage = message.usage;
    if (!usage || !usage.total_tokens) return null;

    return (
      <Box mt={1} ml={2}>
        <HStack gap={2} fontSize="xs" color={mutedTextColor} flexWrap="wrap">
          <Text>
            <Text as="span" fontWeight="medium">
              Input:
            </Text>{' '}
            {usage.prompt_tokens || 0}
          </Text>
          <Text>
            <Text as="span" fontWeight="medium">
              Output:
            </Text>{' '}
            {usage.completion_tokens || 0}
          </Text>
          {usage.reasoning_tokens && (
            <Text>
              <Text as="span" fontWeight="medium">
                Reasoning:
              </Text>{' '}
              {usage.reasoning_tokens}
            </Text>
          )}
          {message.cost && (
            <Text>
              <Text as="span" fontWeight="medium">
                Cost:
              </Text>{' '}
              {pricingService.formatCost(message.cost)}
            </Text>
          )}
        </HStack>
      </Box>
    );
  };

  const renderMessage = (message: SharedChatMessage) => {
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
                opacity={
                  Array.isArray(message.tool_calls) && message.tool_calls.length > 0
                    ? 0.7
                    : 1
                }
              >
                <Card.Body p={3}>
                  {message.content ? (
                    <Text fontSize="sm" whiteSpace="pre-wrap">
                      {message.content}
                    </Text>
                  ) : Array.isArray(message.tool_calls) &&
                    message.tool_calls.length > 0 ? (
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
                              Name: {toolCall.name}
                            </Text>
                            <Text fontSize="sm" color={mutedTextColor} mt={1}>
                              Parameters:
                            </Text>
                            <Box p={2} bg={toolResultBg} borderRadius="md" mt={1}>
                              <Text
                                fontSize="xs"
                                fontFamily="mono"
                                color={mutedTextColor}
                              >
                                {JSON.stringify(toolCall.arguments, null, 2)}
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
                {message.inference_time_ms
                  ? formatInferenceTime(message.inference_time_ms)
                  : formatTimestamp(message.timestamp)}
              </Text>
              {renderTokenMetrics(message)}
              {!message.content && !(Array.isArray(message.tool_calls) && message.tool_calls.length > 0) && (
                <Box mt={2} ml={2} p={2} bg="orange.50" borderRadius="md" borderWidth="1px" borderColor="orange.200" _dark={{ bg: 'orange.900/20', borderColor: 'orange.700' }}>
                  <Text fontSize="xs" color="orange.700" _dark={{ color: 'orange.300' }}>
                    The model was unable to generate a response. This may have been due to the max tokens limit.
                  </Text>
                </Box>
              )}
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
              <Text
                fontSize="xs"
                color={timestampColor}
                mt={1}
                mr={2}
                textAlign="right"
              >
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
          <CollapsibleSystemMessage
            content={message.content}
            timestamp={message.timestamp}
            formatTimestamp={formatTimestamp}
          />
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
                </Card.Body>
              </Card.Root>
              <Text
                fontSize="xs"
                color={timestampColor}
                mt={1}
                mr={2}
                textAlign="right"
              >
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
    <Box flex={1} display="flex" flexDirection="column" minH={0} overflow="hidden">
      <Box
        ref={scrollAreaRef}
        flex={1}
        p={4}
        overflowY="auto"
        overflowX="hidden"
        minH={0}
        css={{
          scrollBehavior: 'smooth',
          '&::-webkit-scrollbar': {
            width: '8px',
          },
          '&::-webkit-scrollbar-track': {
            background: 'transparent',
          },
          '&::-webkit-scrollbar-thumb': {
            background: 'var(--chakra-colors-bg-muted)',
            borderRadius: '4px',
          },
        }}
      >
        {messages.length === 0 ? (
          <VStack justify="center" align="center" h="full" color={mutedTextColor}>
            <LuBot size={48} opacity={0.3} />
            <Text fontSize="sm">No messages in this conversation.</Text>
          </VStack>
        ) : (
          <VStack gap={0} align="stretch">
            {messages.map((message) => (
              <React.Fragment key={message.id}>
                {renderMessage(message)}
              </React.Fragment>
            ))}
          </VStack>
        )}
      </Box>
    </Box>
  );
}
