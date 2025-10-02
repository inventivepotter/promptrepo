'use client';

import React from 'react';
import {
  HStack,
  VStack,
  Text,
  Button,
  Box,
} from '@chakra-ui/react';
import { LuArrowLeft } from 'react-icons/lu';
import { useFormData } from '@/stores/promptStore/hooks';

interface PromptEditorHeaderProps {
  onBack: () => void;
  onSave: () => void;
  canSave: boolean;
  isSaving?: boolean;
}

export function PromptEditorHeader({ onBack, onSave, canSave, isSaving = false }: PromptEditorHeaderProps) {
  const formData = useFormData();

  return (
    <Box
      py={4}
      px={6}
      position="sticky"
      top={0}
      zIndex={10}
      bg="bg.subtle"
    >
      <HStack justify="space-between" align="center">
        <HStack gap={4}>
          <Button
            variant="outline"
            onClick={onBack}
            size="sm"
          >
            <HStack gap={2}>
              <LuArrowLeft size={16} />
              <Text>Back</Text>
            </HStack>
          </Button>
          <VStack align="start" gap={1}>
            <Text
              color="fg.muted"
              fontSize="2xl"
              letterSpacing="tight"
              fontWeight="1000"
            >
              {formData.name || 'New Prompt'}
            </Text>
            <Text fontSize="sm" opacity={0.7}>
              Edit prompt settings and configuration. Click Save to persist changes.
            </Text>
          </VStack>
        </HStack>
        <HStack gap={3}>
          <Button
            colorScheme="blue"
            onClick={onSave}
            disabled={!canSave || isSaving}
            loading={isSaving}
          >
            {isSaving ? 'Saving...' : 'Save Prompt'}
          </Button>
        </HStack>
      </HStack>
    </Box>
  );
}