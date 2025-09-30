'use client';

import React from 'react';
import {
  Box,
  HStack,
  VStack,
  Text,
  Badge,
  Button,
  Card,
} from '@chakra-ui/react';
import { LuPencil, LuTrash, LuClock } from 'react-icons/lu';
import { useColorModeValue } from '../../../components/ui/color-mode';
import { Prompt } from '@/types/Prompt';

interface PromptCardProps {
  prompt: Prompt;
  onEdit: (prompt: Prompt) => void;
  onDelete: (id: string) => void;
}

export function PromptCard({ prompt, onEdit, onDelete }: PromptCardProps) {
  // Theme-aware colors
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const mutedTextColor = useColorModeValue('gray.600', 'gray.400');
  const hoverBg = useColorModeValue('gray.50', 'gray.700');
  const cardBg = useColorModeValue('gray.50', 'gray.900');
  const promptPreviewBg = useColorModeValue('gray.100', 'gray.800');
  const promptBorderColor = useColorModeValue('blue.200', 'blue.200');

  const formatDate = (date: Date) => {
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  };

  const truncateText = (text: string, maxLength: number) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  return (
    <Card.Root
      bg={cardBg}
      borderColor={borderColor}
      _hover={{ transform: 'translateY(-2px)', shadow: 'md' }}
      transition="all 0.2s ease"
      cursor="pointer"
      onClick={() => onEdit(prompt)}
    >
      <Card.Body p={4}>
        <VStack align="stretch" gap={3}>
          <HStack justify="space-between" align="start">
            <VStack align="stretch" flex={1} gap={2}>
              <Text fontSize="lg" fontWeight="semibold" lineClamp={1}>
                {prompt.name || 'Untitled Prompt'}
              </Text>
              <Text fontSize="sm" color={mutedTextColor} lineClamp={2}>
                {truncateText(prompt.description || 'No description provided', 120)}
              </Text>
            </VStack>
            <HStack gap={1}>
              <Button
                size="sm"
                variant="ghost"
                onClick={(e) => {
                  e.stopPropagation();
                  onEdit(prompt);
                }}
                _hover={{ bg: hoverBg }}
              >
                <LuPencil size={14} />
              </Button>
              <Button
                size="sm"
                variant="ghost"
                colorPalette="red"
                onClick={(e) => {
                  e.stopPropagation();
                  onDelete(prompt.id);
                }}
                _hover={{ bg: 'red.50' }}
              >
                <LuTrash size={14} />
              </Button>
            </HStack>
          </HStack>

          <HStack justify="space-between" align="center" flexWrap="wrap" gap={2}>
            <HStack gap={2} flexWrap="wrap">
              {prompt.repo_name && (
                <Badge size="sm" variant="subtle" colorPalette="green">
                  {prompt.repo_name}
                </Badge>
              )}
              {prompt.category && (
                <Badge size="sm" variant="subtle" colorPalette="blue">
                  {prompt.category}
                </Badge>
              )}
              {prompt.tags && prompt.tags.length > 0 && (
                <>
                  {prompt.tags.slice(0, 3).map((tag, index) => (
                    <Badge key={index} size="sm" variant="subtle" colorPalette="purple">
                      {tag}
                    </Badge>
                  ))}
                  {prompt.tags.length > 3 && (
                    <Badge size="sm" variant="subtle" colorPalette="gray">
                      +{prompt.tags.length - 3}
                    </Badge>
                  )}
                </>
              )}
            </HStack>

            <HStack gap={1} fontSize="xs" color={mutedTextColor}>
              <LuClock size={12} />
              <Text>{formatDate(new Date(prompt.updated_at))}</Text>
            </HStack>
          </HStack>

          {prompt.content && (
            <Box
              p={3}
              bg={promptPreviewBg}
              borderRadius="md"
              borderLeft="3px solid"
              borderColor={promptBorderColor}
            >
              <Text fontSize="sm" color={mutedTextColor} lineClamp={3}>
                {truncateText(prompt.content, 150)}
              </Text>
            </Box>
          )}
        </VStack>
      </Card.Body>
    </Card.Root>
  );
}