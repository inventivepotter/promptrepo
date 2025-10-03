'use client';

import React from 'react';
import {
  Box,
  VStack,
} from '@chakra-ui/react';
import { useColorModeValue } from '@/components/ui/color-mode';
import { ChatMessages } from './ChatMessages';
import { ChatInput } from './ChatInput';
import { ChatFooter } from './ChatFooter';
import { ChatSimpleHeader } from './ChatSimpleHeader';
import { TokenStats } from './TokenStats';
import { Tool } from '../_types/ChatState';
import { useChatInput, useMessages, useIsSending, useChatActions } from '@/stores/chatStore/hooks';

interface ChatProps {
  // Optional props for customization
  height?: string;
  onMessageSend?: (message: string, tools: string[]) => void;
}

export function Chat({ height = "700px", onMessageSend }: ChatProps) {
  // Use chatStore hooks
  const messages = useMessages();
  const isSending = useIsSending();
  const { inputMessage, setInputMessage } = useChatInput();
  const { sendMessage, clearMessages, clearInput, stopStreaming } = useChatActions();
  
  const [selectedTools, setSelectedTools] = React.useState<string[]>([]);

  // Mock tools data - in real implementation this would come from API
  const mockTools: Tool[] = [
    {
      id: 'search_files',
      name: 'Search Files',
      description: 'Search for text patterns across files in the project'
    },
    {
      id: 'read_file',
      name: 'Read File',
      description: 'Read the contents of a specific file'
    },
    {
      id: 'write_to_file',
      name: 'Write to File',
      description: 'Create or modify files with new content'
    },
    {
      id: 'execute_command',
      name: 'Execute Command',
      description: 'Run terminal commands and scripts'
    },
    {
      id: 'browser_action',
      name: 'Browser Action',
      description: 'Interact with web pages using a browser'
    },
  ];

  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const bgColor = useColorModeValue('white', 'gray.800');
  const handleReset = () => {
    // Clear messages using store actions
    clearMessages();
    clearInput();
    setSelectedTools([]);
  };

  const handleSendMessage = async (message: string) => {
    // Call the optional callback
    if (onMessageSend) {
      onMessageSend(message, selectedTools);
    }

    // Use the store's sendMessage action
    await sendMessage(message);
  };
  // Calculate total tokens from all messages
  const calculateTotalTokens = () => {
    let totalInput = 0;
    let totalOutput = 0;
    
    messages.forEach(message => {
      if (message.usage) {
        totalInput += message.usage.prompt_tokens || 0;
        totalOutput += message.usage.completion_tokens || 0;
      }
    });
    
    return { totalInput, totalOutput };
  };

  const { totalInput, totalOutput } = calculateTotalTokens();

  return (
    <Box
      borderWidth="1px"
      borderColor={borderColor}
      borderRadius="md"
      bg={bgColor}
      overflow="hidden"
    >
      <Box
        height={height}
        display="flex"
        flexDirection="column"
        overflow="hidden"
      >
        <VStack gap={0} align="stretch" height="full">
          {/* Header - Agent title and reset functionality */}
          <ChatSimpleHeader
            onReset={handleReset}
            isLoading={isSending}
            messages={messages}
          />

          {/* Token Stats at the top */}
          <TokenStats
            totalInputTokens={totalInput}
            totalOutputTokens={totalOutput}
          />

          {/* Messages */}
          <Box flex={1} overflow="hidden" minHeight="300px">
            <ChatMessages
              messages={messages}
              isLoading={isSending}
            />
          </Box>

          {/* Input */}
          <ChatInput
            value={inputMessage}
            onChange={setInputMessage}
            onSubmit={handleSendMessage}
            onStop={stopStreaming}
            isLoading={isSending}
            disabled={false}
            placeholder="Type your message here..."
            totalInputTokens={totalInput}
            totalOutputTokens={totalOutput}
          />
        </VStack>
      </Box>

      {/* Footer - tools only - Outside height constraint so it gets pushed down */}
      <ChatFooter
        selectedTools={selectedTools}
        availableTools={mockTools}
        onToolsChange={setSelectedTools}
      />
    </Box>
  );
}