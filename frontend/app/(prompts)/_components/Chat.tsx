'use client';

import React from 'react';
import {
  Box,
  VStack,
  Text,
  Textarea,
} from '@chakra-ui/react';
import { useColorModeValue } from '../../../components/ui/color-mode';
import { ChatMessages } from './ChatMessages';
import { ChatInput } from './ChatInput';
import { ChatFooter } from './ChatFooter';
import { ChatSimpleHeader } from './ChatSimpleHeader';
import { TokenStats } from './TokenStats';
import { TemplateVariables } from './TemplateVariables';
import { ChatState, Tool } from '../_types/ChatState';
import { chatCompletion } from '../_lib/chatCompletion';
import { createUserMessage, createAssistantMessage, toOpenAIMessages } from '../_lib/utils/messageUtils';
import { usePromptsState } from '../_state/promptState';
import type { ChatCompletionOptions } from '../_types/ChatApi';
import { extractVariables, resolveTemplate, hasVariables } from '../_lib/utils/templateUtils';

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

export function Chat({ height = "700px", onMessageSend, promptData }: ChatProps) {
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
  const [templateVariables, setTemplateVariables] = React.useState<Record<string, string>>({});

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
  const mutedTextColor = useColorModeValue('gray.600', 'gray.400');

  // Extract variables from the active prompt template
  const promptTemplate = activePrompt?.prompt || '';
  const extractedVariables = React.useMemo(() => extractVariables(promptTemplate), [promptTemplate]);

  // Initialize template variables when extracted variables change
  React.useEffect(() => {
    const newVariables: Record<string, string> = {};
    extractedVariables.forEach(variable => {
      newVariables[variable] = templateVariables[variable] || '';
    });
    setTemplateVariables(newVariables);
  }, [extractedVariables]);

  // Update a template variable value
  const updateTemplateVariable = (variableName: string, value: string) => {
    setTemplateVariables(prev => ({
      ...prev,
      [variableName]: value
    }));
  };

  // Get resolved template with current variable values
  const resolvedPrompt = React.useMemo(() => {
    if (!hasVariables(promptTemplate)) return promptTemplate;
    return resolveTemplate(promptTemplate, templateVariables);
  }, [promptTemplate, templateVariables]);

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
    // Check if this is the first message and template variables exist
    const isFirstMessage = chatState.messages.length === 0;
    const hasTemplateVariables = extractedVariables.length > 0;
    
    // Validate template variables for first message
    if (isFirstMessage && hasTemplateVariables) {
      const emptyVariables = extractedVariables.filter(variable =>
        !templateVariables[variable] || templateVariables[variable].trim() === ''
      );
      
      if (emptyVariables.length > 0) {
        // Don't proceed - template variables are required for the first message
        return;
      }
    }
    
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

    // Get system message from active prompt (use resolved template if variables exist)
    const systemMessage = hasVariables(promptTemplate) ? resolvedPrompt : activePrompt?.prompt;

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

  // Check if template variables are missing for first message validation
  const isFirstMessage = chatState.messages.length === 0;
  const hasTemplateVariables = extractedVariables.length > 0;
  const missingTemplateVariables = hasTemplateVariables ? extractedVariables.filter(variable =>
    !templateVariables[variable] || templateVariables[variable].trim() === ''
  ) : [];
  const isDisabledDueToTemplateVariables = isFirstMessage && hasTemplateVariables && missingTemplateVariables.length > 0;

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
            disabled={isDisabledDueToTemplateVariables}
            placeholder={isDisabledDueToTemplateVariables
              ? `Complete template variables to send a message`
              : "Type your message here..."
            }
            totalInputTokens={totalInput}
            totalOutputTokens={totalOutput}
          />
        </VStack>
      </Box>

      {/* Template Variables Section - Outside height constraint to expand downward */}
      <TemplateVariables
        promptTemplate={promptTemplate}
        templateVariables={templateVariables}
        onUpdateVariable={updateTemplateVariable}
      />

      {/* Footer - tools only - Outside height constraint so it gets pushed down */}
      <ChatFooter
        selectedTools={chatState.selectedTools}
        availableTools={mockTools}
        onToolsChange={handleToolsChange}
      />
    </Box>
  );
}