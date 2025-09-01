'use client';

import React from 'react';
import {
  Box,
  VStack,
} from '@chakra-ui/react';
import { useColorModeValue } from '../../../components/ui/color-mode';
import { ChatHeader } from './ChatHeader';
import { ChatMessages } from './ChatMessages';
import { ChatInput } from './ChatInput';
import { ChatState, Tool } from '../_types/ChatState';
import { chatCompletion } from '../_lib/chatCompletion';
import { createUserMessage, createAssistantMessage, toOpenAIMessages } from '../_lib/utils/messageUtils';
import { usePromptsState } from '../_state/promptState';
import type { ChatCompletionOptions } from '../_types/ChatApi';

interface ChatProps {
  // Optional props for customization
  height?: string;
  onMessageSend?: (message: string, tools: string[]) => void;
  // Prompt data for chat completion
  promptData?: {
    prompt: string;
    model: string;
    temperature: number;
    max_tokens: number;
    top_p: number;
  };
}

export function Chat({ height = "600px", onMessageSend, promptData }: ChatProps) {
  // Get current prompt from state to access all completion options (fallback)
  const { currentPrompt } = usePromptsState();
  
  // Use provided promptData or fallback to currentPrompt from state
  const activePrompt = promptData || currentPrompt;
  
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
    
    // Create user message using utility function
    const userMessage = createUserMessage(message);

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
    const openAIMessages = toOpenAIMessages(updatedMessages);

    // Build completion options from active prompt (prioritize promptData prop)
    const completionOptions: ChatCompletionOptions | undefined = activePrompt ? {
      provider: activePrompt.model.includes('/')
        ? activePrompt.model.split('/')[0]
        : '',
      model: activePrompt.model.includes('/')
        ? activePrompt.model.split('/').slice(1).join('/')
        : activePrompt.model,
      temperature: activePrompt.temperature,
      max_tokens: activePrompt.max_tokens,
      top_p: activePrompt.top_p,
    } : undefined;

    // Get system message from active prompt
    const systemMessage = activePrompt?.prompt;

    // Call chat completion middleware (handles all errors and notifications)
    const aiMessage = await chatCompletion(openAIMessages, undefined, completionOptions, systemMessage);
    
    if (aiMessage) {
      // Success - add AI response
      setChatState(prev => ({
        ...prev,
        messages: [...prev.messages, aiMessage],
        isLoading: false
      }));
    } else {
      // Error handled by middleware, just add fallback message and stop loading
      const fallbackMessage = createAssistantMessage(
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
          {/* Header - tools and reset functionality */}
          <ChatHeader
            selectedTools={chatState.selectedTools}
            availableTools={mockTools}
            onToolsChange={handleToolsChange}
            onReset={handleReset}
            isLoading={chatState.isLoading}
          />

          {/* Messages */}
          <Box flex={1} overflow="hidden">
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
          />
        </VStack>
      </Box>
    </Box>
  );
}