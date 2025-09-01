'use client';

import React from 'react';
import {
  HStack,
  VStack,
  Text,
  Button,
  Spinner,
} from '@chakra-ui/react';
import { LuArrowLeft, LuGitBranch } from 'react-icons/lu';
import { useColorModeValue } from '@/components/ui/color-mode';
import { Prompt } from '@/types/Prompt';

interface PromptEditorHeaderProps {
  displayPrompt: Prompt;
  onBack: () => void;
  onSave: () => void;
  canSave: boolean;
  isSaving?: boolean;
  onCommitPush?: () => void;
  isCommitPushing?: boolean;
  canCommitPush?: boolean;
}

export function PromptEditorHeader({ displayPrompt, onBack, onSave, canSave, isSaving = false, onCommitPush, isCommitPushing = false, canCommitPush = false }: PromptEditorHeaderProps) {
  const mutedTextColor = useColorModeValue('gray.600', 'gray.400');

  return (
    <HStack justify="space-between" align="center">
      <HStack gap={4}>
        <Button
          variant="ghost"
          onClick={onBack}
          size="sm"
        >
          <HStack gap={2}>
            <LuArrowLeft size={16} />
            <Text>Back</Text>
          </HStack>
        </Button>
        <VStack align="start" gap={1}>
          <Text fontSize="2xl" fontWeight="bold">
            {displayPrompt.name || 'New Prompt'}
          </Text>
          <Text fontSize="sm" color={mutedTextColor}>
            Edit prompt settings and configuration. Click Save to persist changes.
          </Text>
        </VStack>
      </HStack>
      <HStack gap={3}>
        {onCommitPush && (
          <Button
            colorPalette="green"
            variant="outline"
            onClick={onCommitPush}
            disabled={!canCommitPush || isSaving || isCommitPushing}
            loading={isCommitPushing}
          >
            <HStack gap={2}>
              <LuGitBranch size={16} />
              <Text>{isCommitPushing ? 'Committing...' : 'Commit & Push'}</Text>
            </HStack>
          </Button>
        )}
        <Button
          colorScheme="blue"
          onClick={onSave}
          disabled={!canSave || isSaving}
          loading={isSaving}
        >
          <HStack gap={2}>
            {isSaving && <Spinner size="sm" />}
            <Text>{isSaving ? 'Saving...' : 'Save Prompt'}</Text>
          </HStack>
        </Button>
      </HStack>
    </HStack>
  );
}