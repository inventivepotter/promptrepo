'use client';

import React, { useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import {
  Box,
  Container,
  HStack,
  VStack,
  Text,
  Button,
  Select,
  Portal,
  createListCollection,
  Dialog,
} from '@chakra-ui/react';
import { LuPlus, LuX } from 'react-icons/lu';
import { IoRefreshCircle } from "react-icons/io5";
import { useSelectedRepository, useRepositoryFilterActions } from '@/stores/repositoryFilterStore';
import { useUniqueRepositories, usePromptActions, useIsLoading } from '@/stores/promptStore';

export function PromptsHeader() {
  const router = useRouter();
  const headerBg = "bg.subtle";
  const [isGetLatestDialogOpen, setIsGetLatestDialogOpen] = useState(false);
  
  // Use shared repository filter store
  const selectedRepository = useSelectedRepository();
  const { setSelectedRepository } = useRepositoryFilterActions();
  
  // Get available repositories from prompt store
  const availableRepos = useUniqueRepositories();
  
  // Get Latest functionality
  const { getLatestFromBaseBranch } = usePromptActions();
  const isLoading = useIsLoading();

  const handleGetLatest = async () => {
    if (!selectedRepository) return;
    
    try {
      await getLatestFromBaseBranch(selectedRepository);
      setIsGetLatestDialogOpen(false);
    } catch (error) {
      console.error('Failed to get latest from base branch:', error);
    }
  };

  // Create collection for Select component - without "All Repositories" option
  const repoCollection = useMemo(
    () =>
      createListCollection({
        items: availableRepos.map((repo) => ({
          label: repo,
          value: repo,
        })),
      }),
    [availableRepos]
  );

  const handleCreateNew = () => {
    if (selectedRepository) {
      router.push(`/editor?mode=new&repo=${encodeURIComponent(selectedRepository)}`);
    }
  };

  return (
    <>
      <Box
        bg={headerBg}
        borderBottom="1px solid"
        borderColor="bg.muted"
        py={4}
        position="sticky"
        top={0}
        zIndex={10}
      >
        <Container maxW="7xl" mx="auto">
          <HStack justify="space-between" align="center">
            <VStack align="start" gap={1}>
              <Text
                color="fg.muted"
                fontSize="2xl"
                letterSpacing="tight"
                fontWeight="1000"
              >
                Prompts
              </Text>
              <Text fontSize="sm" color="text.secondary">
                Create and manage your AI prompts with version control
              </Text>
            </VStack>
            
            <HStack gap={3} alignItems="flex-end">
              {availableRepos.length > 0 && (
                <Select.Root
                  collection={repoCollection}
                  size="sm"
                  width="240px"
                  value={selectedRepository ? [selectedRepository] : []}
                  onValueChange={(e) => setSelectedRepository(e.value[0] || '')}
                >
                  <Select.Label fontSize="xs">Repository</Select.Label>
                  <Select.HiddenSelect />
                  <Select.Control>
                    <Select.Trigger>
                      <Select.ValueText placeholder="Select Repository" />
                    </Select.Trigger>
                    <Select.IndicatorGroup>
                      <Select.Indicator />
                    </Select.IndicatorGroup>
                  </Select.Control>
                  <Portal>
                    <Select.Positioner>
                      <Select.Content>
                        {repoCollection.items.map((repo) => (
                          <Select.Item item={repo} key={repo.value}>
                            {repo.label}
                            <Select.ItemIndicator />
                          </Select.Item>
                        ))}
                      </Select.Content>
                    </Select.Positioner>
                  </Portal>
                </Select.Root>
              )}
              {selectedRepository && (
                <Button
                  variant="outline"
                  onClick={() => setIsGetLatestDialogOpen(true)}
                  disabled={isLoading}
                  loading={isLoading}
                  padding={0}
                >
                  <IoRefreshCircle size={20} color="var(--chakra-colors-colorPalette-solid)" />
                </Button>
              )}
              <Button
                variant="solid"
                onClick={handleCreateNew}
                disabled={!selectedRepository}
              >
                <LuPlus /> New Prompt
              </Button>
            </HStack>
          </HStack>
        </Container>
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