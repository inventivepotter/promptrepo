'use client';

import React from 'react';
import {
  Box,
  HStack,
  Textarea,
  IconButton,
} from '@chakra-ui/react';
import { LuSend, LuSquare } from 'react-icons/lu';
import { useColorModeValue } from '@/components/ui/color-mode';

interface ChatInputProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: (message: string) => void;
  onStop?: () => void;
  isLoading?: boolean;
  disabled?: boolean;
  placeholder?: string;
  totalInputTokens?: number;
  totalOutputTokens?: number;
}

export function ChatInput({
  value,
  onChange,
  onSubmit,
  onStop,
  isLoading = false,
  disabled = false,
  placeholder = "Type your message here...",
  totalInputTokens = 0,
  totalOutputTokens = 0
}: ChatInputProps) {
  const textareaRef = React.useRef<HTMLTextAreaElement>(null);
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const bgColor = useColorModeValue('white', 'gray.800');

  const handleSubmit = () => {
    const trimmedValue = value.trim();
    if (trimmedValue && !isLoading && !disabled) {
      onSubmit(trimmedValue);
      onChange('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleStop = () => {
    if (onStop) {
      onStop();
    }
  };

  // Auto-resize textarea
  React.useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [value]);

  const canSend = value.trim().length > 0 && !disabled && !isLoading;

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
            ref={textareaRef}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled}
            resize="none"
            minH="40px"
            maxH="120px"
            rows={1}
            borderColor={borderColor}
            fontSize="sm"
            _placeholder={{
              color: useColorModeValue('gray.500', 'gray.400')
            }}
            _focus={{
              borderColor: useColorModeValue('blue.500', 'blue.300'),
              boxShadow: `0 0 0 1px ${useColorModeValue('#3182ce', '#63b3ed')}`
            }}
          />
        </Box>
        
        {isLoading ? (
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
            colorPalette="blue"
            onClick={handleSubmit}
            disabled={!canSend}
            aria-label="Send message"
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
      <Box mt={2} fontSize="xs" color={useColorModeValue('gray.500', 'gray.400')}>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Box>Press Enter to send, Shift+Enter for new line</Box>
          {(totalInputTokens > 0 || totalOutputTokens > 0) && (
            <Box display="flex" gap={4}>
              <Box>Total Input: {totalInputTokens.toLocaleString()}</Box>
              <Box>Total Output: {totalOutputTokens.toLocaleString()}</Box>
            </Box>
          )}
        </Box>
      </Box>
    </Box>
  );
}