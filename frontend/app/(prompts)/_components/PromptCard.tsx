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
import type { PromptMeta } from '@/services/prompts/api';

interface PromptCardProps {
  prompt: PromptMeta;
  onEdit: (prompt: PromptMeta) => void;
  onDelete: (repoName: string, filePath: string, promptName: string) => void;
}

export function PromptCard({ prompt, onEdit, onDelete }: PromptCardProps) {

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
                {prompt.prompt?.name || 'Untitled Prompt'}
              </Text>
              <Text fontSize="sm" opacity={0.6} lineClamp={2}>
                {truncateText(prompt.prompt?.description || 'No description provided', 120)}
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
                _hover={{ bg: 'bg.subtle' }}
              >
                <LuPencil size={14} />
              </Button>
              <Button
                size="sm"
                variant="ghost"
                colorPalette="red"
                onClick={(e) => {
                  e.stopPropagation();
                  onDelete(prompt.repo_name, prompt.file_path, prompt.prompt?.name || 'Untitled Prompt');
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
              {prompt.prompt?.tags && prompt.prompt.tags.length > 0 && (
                <>
                  {prompt.prompt.tags.slice(0, 3).map((tag, index) => (
                    <Badge key={index} size="sm" variant="subtle" colorPalette="purple">
                      {tag}
                    </Badge>
                  ))}
                  {prompt.prompt.tags.length > 3 && (
                    <Badge size="sm" variant="subtle" colorPalette="gray">
                      +{prompt.prompt.tags.length - 3}
                    </Badge>
                  )}
                </>
              )}
            </HStack>

            <HStack gap={1} fontSize="xs" opacity={0.6}>
              <LuClock size={12} />
              <Text>
                {prompt.recent_commits && prompt.recent_commits.length > 0
                  ? formatDate(new Date(prompt.recent_commits[0].timestamp))
                  : prompt.prompt?.updated_at
                    ? formatDate(new Date(prompt.prompt.updated_at))
                    : 'N/A'}
              </Text>
            </HStack>
          </HStack>

          {prompt.prompt?.prompt && (
            <Box
              p={3}
              bg="bg"
              borderRadius="md"
              borderLeft="3px solid"
              borderColor="bg.muted"
            >
              <Text fontSize="sm" opacity={0.6} lineClamp={3}>
                {truncateText(prompt.prompt.prompt, 150)}
              </Text>
            </Box>
          )}
        </VStack>
      </Card.Body>
    </Card.Root>
  );
}