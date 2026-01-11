'use client';

import {
  HStack,
  VStack,
  Text,
  Button,
  Box,
} from '@chakra-ui/react';
import { LuRefreshCw, LuBot, LuChevronDown, LuChevronUp } from 'react-icons/lu';
import { useColorModeValue } from '@/components/ui/color-mode';
import { ShareChatButton } from './ShareChatButton';

interface ChatSimpleHeaderProps {
  onReset: () => void;
  isLoading?: boolean;
  showContent?: boolean;
  onToggleContent?: () => void;
}

export function ChatSimpleHeader({
  onReset,
  isLoading = false,
  showContent = true,
  onToggleContent,
}: ChatSimpleHeaderProps) {
  const mutedTextColor = useColorModeValue('gray.600', 'gray.400');

  return (
    <Box
      p={4}
      borderBottomWidth="1px"
    >
      <VStack gap={3} align="stretch">
        {/* Header with title and action buttons - Always visible */}
        <HStack justify="space-between" align="center">
          <VStack align="start" gap={1}>
            <HStack>
              <LuBot size={18} />
              <Text fontSize="lg" fontWeight="semibold">
                Agent
              </Text>
            </HStack>
            <Text fontSize="xs" color={mutedTextColor}>
              Your playground to test prompts with AI agents
            </Text>
          </VStack>
          <HStack gap={2}>
            <ShareChatButton disabled={isLoading} />
            <Button
              variant="ghost"
              _hover={{ bg: "bg.subtle" }}
              size="sm"
              colorPalette="red"
              onClick={onReset}
              disabled={isLoading}
            >
              <HStack gap={1}>
                <LuRefreshCw size={14} />
                <Text fontSize="xs" fontWeight="medium">Reset</Text>
              </HStack>
            </Button>
            {onToggleContent && (
              <Button
                variant="ghost"
                _hover={{ bg: "bg.subtle" }}
                size="sm"
                onClick={onToggleContent}
                aria-label={showContent ? "Collapse agent section" : "Expand agent section"}
              >
                <HStack gap={1}>
                  <Text fontSize="xs" fontWeight="medium">
                    {showContent ? "Hide" : "Show"}
                  </Text>
                  {showContent ? <LuChevronUp /> : <LuChevronDown />}
                </HStack>
              </Button>
            )}
          </HStack>
        </HStack>
      </VStack>
    </Box>
  );
}