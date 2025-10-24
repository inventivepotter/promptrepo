'use client';

import {
  Box,
  HStack,
  Textarea,
  IconButton,
  Text,
  VStack,
} from '@chakra-ui/react';
import { LuSend, LuSquare } from 'react-icons/lu';
import { useColorModeValue } from '@/components/ui/color-mode';
import { useChatInput, useIsSending, useChatActions, useTokenStats } from '@/stores/chatStore/hooks';

interface ChatInputProps {
  onSubmit?: (message: string) => void;
  placeholder?: string;
  disabled?: boolean;
  disabledMessage?: string;
}

export function ChatInput({
  onSubmit,
  placeholder = "Type your message here...",
  disabled = false,
  disabledMessage,
}: ChatInputProps) {
  const { inputMessage, setInputMessage } = useChatInput();
  const isSending = useIsSending();
  const { stopStreaming, clearInput } = useChatActions();
  const { totalInput, totalOutput } = useTokenStats();
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const bgColor = useColorModeValue('white', 'gray.800');
  const helperTextColor = useColorModeValue('gray.500', 'gray.400');
  const disabledBgColor = useColorModeValue('orange.50', 'orange.900/20');
  const disabledBorderColor = useColorModeValue('orange.200', 'orange.700');
  const disabledTextColor = useColorModeValue('orange.700', 'orange.300');

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
      px={6}
      py={4}
      borderTopWidth="1px"
      borderColor={borderColor}
      bg={bgColor}
    >
      <VStack gap={3} align="stretch">
        {/* Show disabled message when input is disabled */}
        {disabled && disabledMessage && (
          <Box
            p={3}
            bg={disabledBgColor}
            borderWidth="1px"
            borderColor={disabledBorderColor}
          >
            <Text fontSize="sm" color={disabledTextColor} fontWeight="medium">
              {disabledMessage}
            </Text>
          </Box>
        )}
        
        {/* Input container with improved layout */}
        <HStack gap={3} align="flex-start">
          <Box flex={1} position="relative">
            <Textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={inputMessage.trim().length === 0 ? "Type your message (optional) or leave empty to use only the system prompt..." : placeholder}
              disabled={isSending || disabled}
              resize="none"
              h="44px"
              maxH="160px"
              rows={1}
              fontSize="sm"
              px={4}
              py={2}
              borderWidth="1.5px"
              lineHeight="1.5"
              _focus={{
                borderColor: disabled ? disabledBorderColor : 'blue.500',
                boxShadow: disabled ? 'none' : '0 0 0 1px var(--chakra-colors-blue-500)',
              }}
              _disabled={{
                opacity: 0.6,
                cursor: 'not-allowed',
                bg: useColorModeValue('gray.50', 'gray.900'),
              }}
              transition="all 0.2s"
            />
          </Box>
          
          {isSending ? (
            <IconButton
              size="lg"
              colorPalette="red"
              onClick={handleStop}
              aria-label="Stop generation"
              variant="solid"
              h="44px"
              minW="44px"
              _hover={{
                transform: 'scale(1.05)',
              }}
              _active={{
                transform: 'scale(0.95)',
              }}
              transition="all 0.2s"
            >
              <LuSquare size={18} />
            </IconButton>
          ) : (
            <IconButton
              size="lg"
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
              h="44px"
              minW="44px"
              _hover={{
                transform: canSend ? 'scale(1.05)' : 'none',
              }}
              _active={{
                transform: canSend ? 'scale(0.95)' : 'none',
              }}
              _disabled={{
                opacity: 0.5,
                cursor: 'not-allowed',
              }}
              transition="all 0.2s"
            >
              <LuSend size={18} />
            </IconButton>
          )}
        </HStack>
        
        {/* Token stats */}
        {(totalInput > 0 || totalOutput > 0) && (
          <HStack
            fontSize="xs"
            color={helperTextColor}
            justifyContent="flex-end"
            px={1}
            gap={4}
            fontWeight="medium"
          >
            <Text>Input: {totalInput.toLocaleString()}</Text>
            <Text>Output: {totalOutput.toLocaleString()}</Text>
          </HStack>
        )}
      </VStack>
    </Box>
  );
}