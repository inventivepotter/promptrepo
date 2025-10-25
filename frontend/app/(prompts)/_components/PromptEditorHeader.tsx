'use client';

import React from 'react';
import {
  HStack,
  VStack,
  Text,
  Button,
  Box,
  Dialog,
  Portal,
} from '@chakra-ui/react';
import { LuArrowLeft, LuDownload, LuX } from 'react-icons/lu';
import { useCurrentPrompt, usePromptActions, useIsLoading } from '@/stores/promptStore/hooks';

interface PromptEditorHeaderProps {
  onBack: () => void;
  onSave: () => void;
  canSave: boolean;
  isSaving?: boolean;
}

export function PromptEditorHeader({ onBack, onSave, canSave, isSaving = false }: PromptEditorHeaderProps) {
  const currentPrompt = useCurrentPrompt();
  const [isGetLatestDialogOpen, setIsGetLatestDialogOpen] = React.useState(false);
  const { getLatestFromBaseBranch } = usePromptActions();
  const isLoading = useIsLoading();

  const handleGetLatest = async () => {
    if (!currentPrompt?.repo_name) return;
    
    try {
      await getLatestFromBaseBranch(currentPrompt.repo_name);
      setIsGetLatestDialogOpen(false);
    } catch (error) {
      console.error('Failed to get latest from base branch:', error);
    }
  };

  return (
    <>
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
                {currentPrompt?.prompt?.name || 'New Prompt'}
              </Text>
              <Text fontSize="sm" opacity={0.7}>
                Edit prompt settings and configuration. Click Save to push changes and create a PR.
              </Text>
            </VStack>
          </HStack>
          <HStack gap={3}>
            <Button
              variant="outline"
              onClick={() => setIsGetLatestDialogOpen(true)}
              disabled={isLoading}
              loading={isLoading}
            >
              <HStack gap={2}>
                <LuDownload size={12} />
                <Text>Get Latest</Text>
              </HStack>
            </Button>
            <Button
              onClick={onSave}
              disabled={!canSave || isSaving}
              loading={isSaving}
            >
              {isSaving ? 'Saving...' : 'Save Prompt'}
            </Button>
          </HStack>
        </HStack>
      </Box>

      {/* Confirmation Dialog for Get Latest */}
      <Dialog.Root
        open={isGetLatestDialogOpen}
        onOpenChange={(e) => setIsGetLatestDialogOpen(e.open)}
        role="alertdialog"
      >
        <Portal>
          <Dialog.Backdrop />
          <Dialog.Positioner>
            <Dialog.Content>
              <Dialog.Header>
                <Dialog.Title>Get Latest from Base Branch</Dialog.Title>
              </Dialog.Header>
              <Dialog.Body>
                <p>
                  This will fetch all latest prompts from the repository&apos;s configured base branch and will lose any local changes.
                  Changes that have been pushed to the remote repository will still be available in the remote branch.
                  <br /><br />
                  Are you sure you want to continue?
                </p>
              </Dialog.Body>
              <Dialog.Footer>
                <Dialog.ActionTrigger asChild>
                  <Button variant="outline" disabled={isLoading}>
                    Cancel
                  </Button>
                </Dialog.ActionTrigger>
                <Button
                  colorPalette="red"
                  onClick={handleGetLatest}
                  loading={isLoading}
                  disabled={isLoading}
                  ml={3}
                >
                  Get Latest
                </Button>
              </Dialog.Footer>
              <Dialog.CloseTrigger asChild>
                <Button
                  variant="ghost"
                  size="sm"
                  disabled={isLoading}
                  p={2}
                  _hover={{ bg: 'transparent' }}
                  _active={{ bg: 'transparent' }}
                >
                  <LuX size={16} />
                </Button>
              </Dialog.CloseTrigger>
            </Dialog.Content>
          </Dialog.Positioner>
        </Portal>
      </Dialog.Root>
    </>
  );
}