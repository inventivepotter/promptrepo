'use client';

import { useState, useRef, useEffect } from 'react';
import {
  Dialog,
  Portal,
  Button,
  VStack,
  HStack,
  Textarea,
  Checkbox,
  Text,
  Box,
  Spinner,
  IconButton,
} from '@chakra-ui/react';
import { CloseButton } from '@chakra-ui/react';
import { LuSend, LuRefreshCw, LuChevronDown, LuChevronUp } from 'react-icons/lu';
import { FaMagic } from 'react-icons/fa';
import { usePromptOptimizer } from '@/stores/promptimizerStore';

/**
 * Get first N lines of a string
 */
function getFirstLines(text: string, numLines: number): string {
  const lines = text.split('\n');
  if (lines.length <= numLines) return text;
  return lines.slice(0, numLines).join('\n') + '...';
}

interface PromptOptimizerModalProps {
  provider: string;
  model: string;
  currentPrompt: string;
  onApply: (prompt: string) => void;
}

export function PromptOptimizerModal({
  provider,
  model,
  currentPrompt,
  onApply,
}: PromptOptimizerModalProps) {
  const {
    isOpen,
    closeDialog,
    expectsUserMessage,
    setExpectsUserMessage,
    messages,
    isLoading,
    error,
    hasAssistantMessage,
    sendMessage,
    applyPrompt,
    clearConversation,
    reset,
  } = usePromptOptimizer();

  const [inputValue, setInputValue] = useState('');
  const [isPromptExpanded, setIsPromptExpanded] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Check if current prompt needs expansion (more than 2 lines)
  const promptNeedsExpansion = currentPrompt && currentPrompt.trim() && currentPrompt.split('\n').length > 2;

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!inputValue.trim() || isLoading) return;

    const message = inputValue;
    setInputValue('');
    await sendMessage(message, provider, model, currentPrompt);
  };

  const handleApply = () => {
    const optimized = applyPrompt();
    if (optimized) {
      onApply(optimized);
      handleClose();
    }
  };

  const handleClose = () => {
    closeDialog();
    // Reset after closing
    setTimeout(() => {
      reset();
      setInputValue('');
      setIsPromptExpanded(false);
    }, 200);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleClear = () => {
    clearConversation();
    setInputValue('');
  };

  return (
    <Dialog.Root
      open={isOpen}
      onOpenChange={(e) => !e.open && handleClose()}
      size="xl"
    >
      <Portal>
        <Dialog.Backdrop />
        <Dialog.Positioner>
          <Dialog.Content maxH="85vh" maxW="700px">
            <Dialog.Header>
              <HStack gap={2}>
                <FaMagic size={20} />
                <Dialog.Title>Promptimizer</Dialog.Title>
              </HStack>
            </Dialog.Header>

            <Dialog.Body overflowY="auto" px={4}>
              <VStack gap={4} align="stretch">
                {/* Settings */}
                <Box borderWidth="1px" borderRadius="md" p={3} bg="bg.subtle">
                  <Checkbox.Root
                    checked={expectsUserMessage}
                    onCheckedChange={(e) => setExpectsUserMessage(!!e.checked)}
                  >
                    <Checkbox.HiddenInput />
                    <Checkbox.Control />
                    <Checkbox.Label>
                      <VStack align="start" gap={0}>
                        <Text fontWeight="medium" fontSize="sm">
                          Expects user message
                        </Text>
                        <Text fontSize="xs" color="fg.muted">
                          Adds OWASP 2025 prompt injection security guardrails
                        </Text>
                      </VStack>
                    </Checkbox.Label>
                  </Checkbox.Root>
                </Box>

                {/* Chat Messages */}
                <Box
                  borderWidth="1px"
                  borderRadius="md"
                  p={4}
                  minH="300px"
                  maxH="400px"
                  overflowY="auto"
                  bg="bg.muted"
                >
                  <VStack gap={3} align="stretch">
                    {/* Current Prompt as System Message */}
                    {currentPrompt && currentPrompt.trim() && (
                      <Box
                        p={3}
                        borderRadius="md"
                        bg="gray.100"
                        borderWidth="1px"
                        borderColor="gray.200"
                        borderStyle="dashed"
                        opacity={0.8}
                        _dark={{
                          bg: 'gray.700',
                          borderColor: 'gray.600',
                        }}
                        cursor={promptNeedsExpansion ? 'pointer' : 'default'}
                        onClick={() => promptNeedsExpansion && setIsPromptExpanded(!isPromptExpanded)}
                        transition="all 0.2s"
                      >
                        <HStack justify="space-between" align="start">
                          <VStack align="start" gap={1} flex={1}>
                            <Text
                              fontSize="xs"
                              fontWeight="semibold"
                              color="gray.500"
                              _dark={{ color: 'gray.400' }}
                            >
                              Current Prompt
                            </Text>
                            <Text
                              fontSize="xs"
                              color="gray.600"
                              fontFamily="mono"
                              whiteSpace="pre-wrap"
                              wordBreak="break-word"
                              _dark={{ color: 'gray.300' }}
                            >
                              {isPromptExpanded ? currentPrompt : getFirstLines(currentPrompt, 3)}
                            </Text>
                          </VStack>
                          {promptNeedsExpansion && (
                            <IconButton
                              aria-label={isPromptExpanded ? 'Collapse' : 'Expand'}
                              size="2xs"
                              variant="ghost"
                              onClick={(e) => {
                                e.stopPropagation();
                                setIsPromptExpanded(!isPromptExpanded);
                              }}
                            >
                              {isPromptExpanded ? <LuChevronUp /> : <LuChevronDown />}
                            </IconButton>
                          )}
                        </HStack>
                      </Box>
                    )}

                    {/* Empty State or Messages */}
                    {messages.length === 0 ? (
                      <VStack gap={2} py={6}>
                        <FaMagic size={32} opacity={0.3} />
                        <Text color="fg.muted" fontSize="sm" textAlign="center">
                          {currentPrompt && currentPrompt.trim()
                            ? 'Tell me how you want to enhance your current prompt...'
                            : 'Describe your prompt idea to get started...'}
                        </Text>
                        <Text color="fg.muted" fontSize="xs" textAlign="center">
                          {currentPrompt && currentPrompt.trim()
                            ? 'Example: "Make it more concise" or "Add error handling instructions"'
                            : 'Example: "A helpful customer service agent that handles product returns"'}
                        </Text>
                      </VStack>
                    ) : (
                      <>
                        {messages.map((msg) => (
                          <Box
                            key={msg.id}
                            p={3}
                            borderRadius="md"
                            bg={msg.role === 'user' ? 'blue.50' : 'white'}
                            borderWidth={msg.role === 'assistant' ? '1px' : '0'}
                            borderColor="gray.200"
                            alignSelf={
                              msg.role === 'user' ? 'flex-end' : 'flex-start'
                            }
                            maxW={msg.role === 'user' ? '80%' : '100%'}
                            _dark={{
                              bg: msg.role === 'user' ? 'blue.900' : 'gray.800',
                              borderColor: 'gray.600',
                            }}
                          >
                            <Text
                              fontSize="xs"
                              fontWeight="semibold"
                              mb={1}
                              color={msg.role === 'user' ? 'blue.600' : 'gray.600'}
                              _dark={{
                                color:
                                  msg.role === 'user' ? 'blue.300' : 'gray.400',
                              }}
                            >
                              {msg.role === 'user' ? 'You' : 'Promptimizer'}
                            </Text>
                            <Text
                              fontSize="sm"
                              whiteSpace="pre-wrap"
                              fontFamily={
                                msg.role === 'assistant' ? 'mono' : 'inherit'
                              }
                            >
                              {msg.content}
                            </Text>
                          </Box>
                        ))}
                        {isLoading && (
                          <HStack gap={2} p={3}>
                            <Spinner size="sm" />
                            <Text fontSize="sm" color="fg.muted">
                              Optimizing your prompt...
                            </Text>
                          </HStack>
                        )}
                      </>
                    )}
                    <div ref={messagesEndRef} />
                  </VStack>
                </Box>

                {/* Error Display */}
                {error && (
                  <Box
                    p={3}
                    borderRadius="md"
                    bg="red.50"
                    borderWidth="1px"
                    borderColor="red.200"
                    _dark={{ bg: 'red.900', borderColor: 'red.700' }}
                  >
                    <Text color="red.600" fontSize="sm" _dark={{ color: 'red.300' }}>
                      {error}
                    </Text>
                  </Box>
                )}

                {/* Input */}
                <HStack gap={2}>
                  <Textarea
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder={
                      messages.length === 0
                        ? 'Describe your prompt idea...'
                        : 'Ask for refinements or changes...'
                    }
                    rows={2}
                    resize="none"
                    disabled={isLoading}
                  />
                  <VStack>
                    <IconButton
                      aria-label="Send message"
                      onClick={handleSend}
                      disabled={!inputValue.trim() || isLoading}
                      colorPalette="blue"
                      size="sm"
                    >
                      <LuSend />
                    </IconButton>
                    {messages.length > 0 && (
                      <IconButton
                        aria-label="Clear conversation"
                        onClick={handleClear}
                        disabled={isLoading}
                        variant="ghost"
                        size="sm"
                      >
                        <LuRefreshCw />
                      </IconButton>
                    )}
                  </VStack>
                </HStack>

                {/* Help Text */}
                <Text fontSize="xs" color="fg.muted">
                  Provider: {provider} | Model: {model}
                </Text>
              </VStack>
            </Dialog.Body>

            <Dialog.Footer gap={2}>
              <Button variant="outline" onClick={handleClose} disabled={isLoading}>
                Cancel
              </Button>
              <Button
                colorPalette="green"
                onClick={handleApply}
                disabled={!hasAssistantMessage || isLoading}
              >
                Apply System Prompt
              </Button>
            </Dialog.Footer>

            <Dialog.CloseTrigger asChild>
              <CloseButton size="sm" disabled={isLoading} />
            </Dialog.CloseTrigger>
          </Dialog.Content>
        </Dialog.Positioner>
      </Portal>
    </Dialog.Root>
  );
}
