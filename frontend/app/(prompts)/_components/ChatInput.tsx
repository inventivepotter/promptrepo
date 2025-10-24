'use client';

import {
  Box,
  HStack,
  Textarea,
  IconButton,
} from '@chakra-ui/react';
import { LuSend, LuSquare } from 'react-icons/lu';
import { useColorModeValue } from '@/components/ui/color-mode';
import { useChatInput, useIsSending, useChatActions, useTokenStats } from '@/stores/chatStore/hooks';

interface ChatInputProps {
  onSubmit?: (message: string) => void;
  placeholder?: string;
  disabled?: boolean;
}

export function ChatInput({
  onSubmit,
  placeholder = "Type your message here...",
  disabled = false,
}: ChatInputProps) {
  const { inputMessage, setInputMessage } = useChatInput();
  const isSending = useIsSending();
  const { stopStreaming, clearInput } = useChatActions();
  const { totalInput, totalOutput } = useTokenStats();
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const bgColor = useColorModeValue('white', 'gray.800');
  const helperTextColor = useColorModeValue('gray.500', 'gray.400');

  const handleSubmit = () => {
    const trimmedValue = inputMessage.trim();
    // Allow submission even with empty message
    if (!isSending && !disabled) {
      // Always call onSubmit if provided, otherwise this is a no-op
      // This prevents message loss when onSubmit is not provided
      if (onSubmit) {
        // Pass empty string if no message (system-only mode)
        onSubmit(trimmedValue || '');
        clearInput();
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleStop = () => {
    stopStreaming();
  };

  // Fix: canSend should be true only when not sending AND not disabled
  // This properly reflects when the user can actually send a message
  const canSend = !isSending && !disabled;

  return (
    <Box
      p={4}
      borderTopWidth="1px"
      borderColor={borderColor}
      bg={bgColor}
    >
      <HStack gap={2} align="center">
        <Box flex={1}>
          <Textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={inputMessage.trim().length === 0 ? "Type your message (optional) or leave empty to use only the system prompt..." : placeholder}
            disabled={isSending || disabled}
            resize="none"
            minH="40px"
            maxH="120px"
            rows={1}
            fontSize="sm"
          />
        </Box>
        
        {isSending ? (
          <IconButton
            size="sm"
            colorPalette="red"
            onClick={handleStop}
            aria-label="Stop generation"
            variant="solid"
            h="40px"
            minW="40px"
            mt="-5px"
          >
            <LuSquare size={16} />
          </IconButton>
        ) : (
          <IconButton
            size="sm"
            colorPalette={disabled ? "gray" : "blue"}
            onClick={handleSubmit}
            disabled={!canSend}
            aria-label={
              disabled
                ? "Fill in all variables to send"
                : inputMessage.trim().length === 0
                  ? "Send with system prompt only"
                  : "Send message"
            }
            variant="solid"
            h="40px"
            mt="-5px"
            minW="40px"
          >
            <LuSend size={16} />
          </IconButton>
        )}
      </HStack>
      
      {/* Helper text and token stats */}
      <Box mt={2} fontSize="xs" color={helperTextColor}>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Box>
            Press Enter to send{inputMessage.trim().length === 0 && ' (system-only mode)'}, Shift+Enter for new line
          </Box>
          {(totalInput > 0 || totalOutput > 0) && (
            <Box display="flex" gap={4}>
              <Box>Total Input: {totalInput.toLocaleString()}</Box>
              <Box>Total Output: {totalOutput.toLocaleString()}</Box>
            </Box>
          )}
        </Box>
      </Box>
    </Box>
  );
}