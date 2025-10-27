'use client';

import { useState } from 'react';
import {
  Box,
  VStack,
  Collapsible,
} from '@chakra-ui/react';
import { useColorModeValue } from '@/components/ui/color-mode';
import { ChatMessages } from './ChatMessages';
import { ChatInput } from './ChatInput';
import { ChatSimpleHeader } from './ChatSimpleHeader';
import { TokenStats } from './TokenStats';
import { TemplateVariables } from './TemplateVariables';
import {
  useMessages,
  useIsSending,
  useChatActions,
  useTemplateVariables,
} from '@/stores/chatStore/hooks';
import { useCurrentPrompt } from '@/stores/promptStore/hooks';
import { TemplateUtils } from '@/services/prompts';

interface ChatProps {
  // Optional props for customization
  height?: string;
  onMessageSend?: (message: string, tools: string[]) => void;
}


export function Chat({ height = "700px", onMessageSend }: ChatProps) {
  // Use chatStore hooks
  const messages = useMessages();
  const isSending = useIsSending();
  const { sendMessage, clearMessages, clearInput, setTemplateVariable, clearTemplateVariables } = useChatActions();
  const templateVariables = useTemplateVariables();
  
  // Use promptStore hooks to get current prompt
  const currentPrompt = useCurrentPrompt();
  
  // State for showing/hiding chat content
  const [showChatContent, setShowChatContent] = useState(true);
  // State to track if first message has been sent (to collapse variables after)
  const [hasStartedChat, setHasStartedChat] = useState(false);
  // State to control if template variables panel is expanded
  const [variablesExpanded, setVariablesExpanded] = useState(true);

  const borderColor = "bg.muted";
  const bgColor = useColorModeValue('white', 'gray.800');
  
  // Check if all required variables are filled
  const requiredVariables = currentPrompt?.prompt?.prompt
    ? TemplateUtils.extractVariables(currentPrompt.prompt.prompt)
    : [];
  const allVariablesFilled = requiredVariables.length === 0 ||
    requiredVariables.every(varName => templateVariables[varName]?.trim());
  
  const handleReset = () => {
    clearMessages();
    clearInput();
    clearTemplateVariables();
  };

  const handleSendMessage = async (message: string) => {
    // Mark that chat has started and collapse variables panel
    setHasStartedChat(true);
    setVariablesExpanded(false);
    
    // Resolve template variables if current prompt has variables
    let systemPrompt: string | undefined = undefined;
    
    if (currentPrompt?.prompt?.prompt && TemplateUtils.hasVariables(currentPrompt.prompt.prompt)) {
      // Resolve the template with the current variables
      systemPrompt = TemplateUtils.resolveTemplate(currentPrompt.prompt.prompt, templateVariables);
    } else if (currentPrompt?.prompt?.prompt) {
      // Use the prompt as-is if no variables
      systemPrompt = currentPrompt.prompt.prompt;
    }
    
    // Get tools from prompt metadata
    const promptTools = currentPrompt?.prompt?.tools || [];
    
    if (onMessageSend) {
      onMessageSend(message, promptTools);
    }
    
    // Get model config from current prompt if available
    const modelConfig = currentPrompt?.prompt?.provider && currentPrompt?.prompt?.model ? {
      provider: currentPrompt.prompt.provider,
      model: currentPrompt.prompt.model,
      temperature: currentPrompt.prompt.temperature,
    } : undefined;
    
    // Create promptId from repo_name and file_path (format: repo_name:file_path)
    const promptId = currentPrompt?.repo_name && currentPrompt?.file_path
      ? `${currentPrompt.repo_name}:${currentPrompt.file_path}`
      : undefined;
    
    // Get repo_name to send separately for tool loading
    const repoName = currentPrompt?.repo_name;
    
    await sendMessage(message, {
      systemPrompt,
      modelConfig,
      promptId,
      repoName,
      tools: promptTools, // Pass prompt tools to chat store
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
      {/* Header - Always visible */}
      <ChatSimpleHeader
        onReset={handleReset}
        isLoading={isSending}
        showContent={showChatContent}
        onToggleContent={() => setShowChatContent(!showChatContent)}
      />

      {/* Collapsible content - Everything except header */}
      <Collapsible.Root open={showChatContent}>
        <Collapsible.Content>
          <VStack gap={0} align="stretch" height={height}>
            {/* Token Stats at the top */}
            <TokenStats />

            {/* Messages - Takes remaining space */}
            <Box flex={1} overflow="hidden" minHeight="200px">
              <ChatMessages
                messages={messages}
                isLoading={isSending}
              />
            </Box>

            {/* Template Variables - Collapsible panel */}
            {currentPrompt?.prompt?.prompt && TemplateUtils.hasVariables(currentPrompt.prompt.prompt) && (
              <TemplateVariables
                promptTemplate={currentPrompt.prompt.prompt}
                templateVariables={templateVariables}
                onUpdateVariable={setTemplateVariable}
                isExpanded={variablesExpanded}
                onToggle={() => setVariablesExpanded(!variablesExpanded)}
              />
            )}

            {/* Input - Always visible */}
            <ChatInput
              onSubmit={handleSendMessage}
              disabled={!allVariablesFilled && requiredVariables.length > 0}
            />
          </VStack>
        </Collapsible.Content>
      </Collapsible.Root>
    </Box>
  );
}