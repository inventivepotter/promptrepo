'use client';

import React from 'react';
import {
  Box,
  VStack,
  Collapsible,
  HStack,
  Text,
} from '@chakra-ui/react';
import { FaChevronDown, FaChevronUp } from 'react-icons/fa';
import { GiMagicLamp } from 'react-icons/gi';
import { useColorModeValue } from '../../../components/ui/color-mode';
import { ChatHeader } from './ChatHeader';
import { ChatMessages } from './ChatMessages';
import { ChatInput } from './ChatInput';
import { ChatMessage, ChatState, Tool } from '../_types/ChatState';

interface ChatProps {
  // Optional props for customization
  height?: string;
  onMessageSend?: (message: string, tools: string[]) => void;
}

export function Chat({ height = "600px", onMessageSend }: ChatProps) {
  const [isOpen, setIsOpen] = React.useState(true);
  
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

  const handleSendMessage = (message: string) => {
    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      type: 'user',
      content: message,
      timestamp: new Date(),
    };

    // Add user message
    setChatState(prev => ({
      ...prev,
      messages: [...prev.messages, userMessage],
      isLoading: true
    }));

    // Call the optional callback
    if (onMessageSend) {
      onMessageSend(message, chatState.selectedTools);
    }

    // Simulate AI response (in real implementation this would be an API call)
    setTimeout(() => {
      const aiMessage: ChatMessage = {
        id: `ai-${Date.now()}`,
        type: 'ai',
        content: `🧪 **Testing your prompt...**\n\nReceived: "${message}"\n\nTools enabled: ${chatState.selectedTools.length > 0 ? chatState.selectedTools.join(', ') : 'none'}\n\n✨ This is where your AI agent would respond using the prompt configuration from the left panel. Connect your backend to see real responses!`,
        timestamp: new Date(),
      };

      setChatState(prev => ({
        ...prev,
        messages: [...prev.messages, aiMessage],
        isLoading: false
      }));
    }, 1000);
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
      <Collapsible.Root open={isOpen} onOpenChange={(e) => setIsOpen(e.open)}>
        <Collapsible.Trigger asChild>
          <Box
            cursor="pointer"
            p={3}
          >
            <HStack justify="space-between" align="center">
              <HStack>
                <GiMagicLamp size={18} />
                <Text fontSize="lg" fontWeight="semibold">
                  Ask Genie!
                </Text>
              </HStack>
              {isOpen ? <FaChevronUp size={14} /> : <FaChevronDown size={14} />}
            </HStack>
          </Box>
        </Collapsible.Trigger>
        <Collapsible.Content>
          <Box
            height={height}
            display="flex"
            flexDirection="column"
            overflow="hidden"
            mt={0}
          >
            <VStack gap={0} align="stretch" height="full">
              {/* Header - now without title since it's in the collapsible trigger */}
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
        </Collapsible.Content>
      </Collapsible.Root>
    </Box>
  );
}