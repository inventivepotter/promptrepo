'use client';

import React, { useState } from 'react';
import {
  Button,
  Dialog,
  Portal,
} from '@chakra-ui/react';
import { LuX } from 'react-icons/lu';
import { IoRefreshCircle } from "react-icons/io5";
import ReposApi from '@/services/repos/api';

interface GetLatestButtonProps {
  /** The repository name to fetch latest from */
  repoName: string | null;
  /** Whether the button should be disabled */
  disabled?: boolean;
  /** Callback function after successfully getting latest */
  onSuccess?: () => Promise<void>;
  /** The artifact type (for display in the dialog) */
  artifactType?: 'prompts' | 'tests' | 'tools' | 'test suites' | 'artifacts';
}

/**
 * Generic Get Latest from Base Branch button component
 * Can be used across all artifact types (prompts, tests, tools, test suites)
 */
export function GetLatestButton({
  repoName,
  disabled = false,
  onSuccess,
  artifactType = 'artifacts',
}: GetLatestButtonProps) {
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleGetLatest = async () => {
    if (!repoName) return;
    
    try {
      setIsLoading(true);
      const result = await ReposApi.getLatestFromBaseBranch(repoName);
      
      // Check for backend soft failures
      const responseData = result as { data?: { status?: string; data?: { success?: boolean; message?: string | undefined } } };
      const status = responseData?.data?.status;
      const op = responseData?.data?.data;
      if (status !== 'success' || op?.success === false) {
        throw new Error(op?.message || responseData?.data?.data?.message || 'Get latest failed');
      }

      // Call the success callback to refresh data
      if (onSuccess) {
        await onSuccess();
      }

      setIsDialogOpen(false);
    } catch (error) {
      console.error('Failed to get latest from base branch:', error);
      // Error is logged, UI can handle via error state if needed
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <Button
        variant="outline"
        onClick={() => setIsDialogOpen(true)}
        disabled={disabled || !repoName}
        loading={isLoading}
        padding={0}
      >
        <IoRefreshCircle size={20} color="var(--chakra-colors-colorPalette-solid)" />
      </Button>

      {/* Confirmation Dialog */}
      <Dialog.Root
        open={isDialogOpen}
        onOpenChange={(e) => setIsDialogOpen(e.open)}
        role="alertdialog"
      >
        <Portal>
          <Dialog.Backdrop />
          <Dialog.Positioner>
            <Dialog.Content>
              <Dialog.Header>
                <Dialog.Title>Reset to Base Branch</Dialog.Title>
              </Dialog.Header>
              <Dialog.Body>
                <p>
                  This will reset all artifacts (prompts, tests, tools, and test suites) in this repository to match the configured base branch.
                  <br /><br />
                  <strong>Warning:</strong> Any local changes that haven&apos;t been pushed to the remote repository will be permanently lost.
                  Changes that have been pushed will remain available in your remote branch.
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
                  Reset to Base Branch
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