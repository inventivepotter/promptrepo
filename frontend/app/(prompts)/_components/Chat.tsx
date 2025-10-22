'use client';

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
import { TemplateVariables } from './TemplateVariables';
import {
  useMessages,
  useIsSending,
  useChatActions,
  useToolsManagement,
  useTemplateVariables,
} from '@/stores/chatStore/hooks';
import { useCurrentPrompt } from '@/stores/promptStore/hooks';
import { TemplateUtils } from '@/services/prompts';

interface ChatProps {
  // Optional props for customization
  height?: string;
  onMessageSend?: (message: string, tools: string[]) => void;
}

// Mock tools data - in real implementation this would come from API
const MOCK_TOOLS = [
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

export function Chat({ height = "700px", onMessageSend }: ChatProps) {
  // Use chatStore hooks
  const messages = useMessages();
  const isSending = useIsSending();
  const { sendMessage, clearMessages, clearInput, setAvailableTools, setTemplateVariable, clearTemplateVariables } = useChatActions();
  const { selectedTools, clearSelectedTools } = useToolsManagement();
  const templateVariables = useTemplateVariables();
  
  // Use promptStore hooks to get current prompt
  const currentPrompt = useCurrentPrompt();

  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const bgColor = useColorModeValue('white', 'gray.800');
  
  // Initialize tools if not already set
  if (useToolsManagement().availableTools.length === 0) {
    setAvailableTools(MOCK_TOOLS);
  }
  
  // Check if all required variables are filled
  const requiredVariables = currentPrompt?.prompt?.prompt
    ? TemplateUtils.extractVariables(currentPrompt.prompt.prompt)
    : [];
  const allVariablesFilled = requiredVariables.length === 0 ||
    requiredVariables.every(varName => templateVariables[varName]?.trim());
  
  const handleReset = () => {
    clearMessages();
    clearInput();
    clearSelectedTools();
    clearTemplateVariables();
  };

  const handleSendMessage = async (message: string) => {
    // Resolve template variables if current prompt has variables
    let systemPrompt: string | undefined = undefined;
    
    if (currentPrompt?.prompt?.prompt && TemplateUtils.hasVariables(currentPrompt.prompt.prompt)) {
      // Resolve the template with the current variables
      systemPrompt = TemplateUtils.resolveTemplate(currentPrompt.prompt.prompt, templateVariables);
    } else if (currentPrompt?.prompt?.prompt) {
      // Use the prompt as-is if no variables
      systemPrompt = currentPrompt.prompt.prompt;
    }
    
    if (onMessageSend) {
      onMessageSend(message, selectedTools);
    }
    
    // Get model config from current prompt if available
    const modelConfig = currentPrompt?.prompt?.provider && currentPrompt?.prompt?.model ? {
      provider: currentPrompt.prompt.provider,
      model: currentPrompt.prompt.model,
      temperature: currentPrompt.prompt.temperature,
    } : undefined;
    
    await sendMessage(message, {
      systemPrompt,
      modelConfig,
    });
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
          {/* Header - Agent title and reset functionality */}
          <ChatSimpleHeader
            onReset={handleReset}
            isLoading={isSending}
          />

          {/* Token Stats at the top */}
          <TokenStats />

          {/* Messages */}
          <Box flex={1} overflow="hidden" minHeight="300px">
            <ChatMessages
              messages={messages}
              isLoading={isSending}
            />
          </Box>

          {/* Input */}
          <ChatInput
            onSubmit={handleSendMessage}
            disabled={!allVariablesFilled}
          />
        </VStack>
      </Box>

      {/* Template Variables - Outside height constraint so it grows downwards */}
      {currentPrompt?.prompt?.prompt && (
        <TemplateVariables
          promptTemplate={currentPrompt.prompt.prompt}
          templateVariables={templateVariables}
          onUpdateVariable={setTemplateVariable}
        />
      )}

      {/* Footer - tools only - Outside height constraint so it gets pushed down */}
      <ChatFooter />
    </Box>
  );
}