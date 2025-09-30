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
import { ChatState, Tool } from '../_types/ChatState';
import { chatService } from '@/services/llm/chat/chatService';
import type { ChatCompletionOptions } from '@/types/Chat';

interface ChatProps {
  // Optional props for customization
  height?: string;
  onMessageSend?: (message: string, tools: string[]) => void;
}

export function Chat({ height = "700px", onMessageSend }: ChatProps) {
  // Chat is now simplified - no prompt data needed
  const activePrompt = undefined;
  
  // Chat state
  const [chatState, setChatState] = React.useState<ChatState>({
    messages: [],
    isLoading: false,
    selectedTools: [],
    availableTools: [
      'search_files',
      'read_file',
      'write_to_file',
      'execute_command',
      'browser_action',
    ],
  });

  const [inputValue, setInputValue] = React.useState('');

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

  // No prompt template functionality for now
  const promptTemplate = '';
  const extractedVariables: string[] = [];

  const handleToolsChange = (tools: string[]) => {
    setChatState(prev => ({
      ...prev,
      selectedTools: tools
    }));
  };

  const handleReset = () => {
    setChatState(prev => ({
      ...prev,
      messages: [],
      isLoading: false
    }));
    setInputValue('');
  };

  const handleSendMessage = async (message: string) => {
    // Create user message using chat service
    const userMessage = chatService.createUserMessage(message);

    // Add user message and set loading state
    const updatedMessages = [...chatState.messages, userMessage];
    setChatState(prev => ({
      ...prev,
      messages: updatedMessages,
      isLoading: true
    }));

    // Call the optional callback
    if (onMessageSend) {
      onMessageSend(message, chatState.selectedTools);
    }

    // Convert messages to OpenAI format for API call
    const openAIMessages = chatService.toOpenAIMessages(updatedMessages);

    // No completion options or system message for now
    const completionOptions: ChatCompletionOptions | undefined = undefined;
    const systemMessage = undefined;

    // Call chat completion middleware (handles all errors and notifications)
    const aiMessage = await chatService.sendChatCompletion(openAIMessages, undefined, completionOptions, systemMessage);
    
    if (aiMessage) {
      // Success - add AI response
      setChatState(prev => ({
        ...prev,
        messages: [...prev.messages, aiMessage],
        isLoading: false
      }));
    } else {
      // Error handled by middleware, just add fallback message and stop loading
      const fallbackMessage = chatService.createAssistantMessage(
        'Unable to get AI response. Please try again.'
      );

      setChatState(prev => ({
        ...prev,
        messages: [...prev.messages, fallbackMessage],
        isLoading: false
      }));
    }
  };

  const handleStopGeneration = () => {
    setChatState(prev => ({
      ...prev,
      isLoading: false
    }));
  };

  // Calculate total tokens from all messages
  const calculateTotalTokens = () => {
    let totalInput = 0;
    let totalOutput = 0;
    
    chatState.messages.forEach(message => {
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
            isLoading={chatState.isLoading}
          />

          {/* Token Stats at the top */}
          <TokenStats
            totalInputTokens={totalInput}
            totalOutputTokens={totalOutput}
          />

          {/* Messages */}
          <Box flex={1} overflow="hidden" minHeight="300px">
            <ChatMessages
              messages={chatState.messages}
              isLoading={chatState.isLoading}
            />
          </Box>

          {/* Input */}
          <ChatInput
            value={inputValue}
            onChange={setInputValue}
            onSubmit={handleSendMessage}
            onStop={handleStopGeneration}
            isLoading={chatState.isLoading}
            disabled={false}
            placeholder="Type your message here..."
            totalInputTokens={totalInput}
            totalOutputTokens={totalOutput}
          />
        </VStack>
      </Box>

      {/* Footer - tools only - Outside height constraint so it gets pushed down */}
      <ChatFooter
        selectedTools={chatState.selectedTools}
        availableTools={mockTools}
        onToolsChange={handleToolsChange}
      />
    </Box>
  );
}