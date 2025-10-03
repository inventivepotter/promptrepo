'use client';

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  VStack,
  Text,
  Grid,
  Box,
  Container,
  ScrollArea,
} from '@chakra-ui/react';
import type { PromptMeta } from '@/services/prompts/api';
import {
  useFilteredPrompts,
  useTotalPrompts,
  useTotalPages,
  useCurrentPage,
  usePromptSearch,
  usePromptSortBy,
  usePromptSortOrder,
  usePromptRepository,
  usePromptActions,
  useUniqueRepositories,
  usePageSize,
  useDeleteDialogOpen,
  usePromptToDelete,
  useIsDeleting,
} from '@/stores/promptStore';
import { PromptSearch } from '../_components/PromptSearch';
import { PromptCard } from '../_components/PromptCard';
import { Pagination } from '../_components/Pagination';
import { PromptsHeader } from '@/components/PromptsHeader';
import { DeletePromptDialog } from '@/components/DeletePromptDialog';

export default function PromptsPage() {
  const router = useRouter();
  
  // Use prompt store hooks
  const filteredPrompts = useFilteredPrompts();
  const totalPrompts = useTotalPrompts();
  const totalPages = useTotalPages();
  const currentPage = useCurrentPage();
  const searchQuery = usePromptSearch();
  const sortBy = usePromptSortBy();
  const sortOrder = usePromptSortOrder();
  const repoFilter = usePromptRepository();
  const availableRepos = useUniqueRepositories();
  const itemsPerPage = usePageSize();
  const {
    fetchPrompts,
    setCurrentPrompt,
    setSearch,
    setPage,
    setSortBy,
    setSortOrder,
    setRepository,
    openDeleteDialog,
    closeDeleteDialog,
    confirmDelete,
  } = usePromptActions();

  // Delete dialog state from store
  const deleteDialogOpen = useDeleteDialogOpen();
  const promptToDelete = usePromptToDelete();
  const isDeleting = useIsDeleting();

  // Manually hydrate the store on client side and fetch prompts
  useEffect(() => {
    // Only run on client side
    if (typeof window !== 'undefined') {
      fetchPrompts();
    }
  }, []);

  const handleEditPrompt = (prompt: PromptMeta) => {
    setCurrentPrompt(prompt);
    router.push(`/editor?repo_name=${encodeURIComponent(prompt.repo_name)}&file_path=${encodeURIComponent(prompt.file_path)}`);
  };

  const handleDeletePrompt = async (repoName: string, filePath: string, promptName: string) => {
    openDeleteDialog(repoName, filePath, promptName);
  };

  const handleSortChange = (newSortBy: 'name' | 'updated_at') => {
    if (newSortBy === sortBy) {
      // Toggle order if same field
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(newSortBy);
      setSortOrder('desc');
    }
  };

  return (
    <Box height="100vh" width="100%" display="flex" flexDirection="column">
        {/* Prompts Header - Outside ScrollArea */}
        <PromptsHeader />

        <ScrollArea.Root flex="1" width="100%">
        <ScrollArea.Viewport
          css={{
            "--scroll-shadow-size": "5rem",
            maskImage:
              "linear-gradient(#000,#000,transparent 0,#000 var(--scroll-shadow-size),#000 calc(100% - var(--scroll-shadow-size)),transparent)",
            "&[data-at-top]": {
              maskImage:
                "linear-gradient(180deg,#000 calc(100% - var(--scroll-shadow-size)),transparent)",
            },
            "&[data-at-bottom]": {
              maskImage:
                "linear-gradient(0deg,#000 calc(100% - var(--scroll-shadow-size)),transparent)",
            },
          }}
        >
          <ScrollArea.Content>
            <Box position="relative">
              <Container maxW="7xl" py={6}>
                <VStack gap={6} align="stretch">
          {/* Search and filters */}
          <PromptSearch
            searchQuery={searchQuery}
            onSearchChange={setSearch}
            sortBy={sortBy || 'updated_at'}
            sortOrder={sortOrder || 'desc'}
            onSortChange={handleSortChange}
            totalPrompts={totalPrompts}
            repoFilter={repoFilter}
            onRepoFilterChange={setRepository}
            availableRepos={availableRepos}
          />

          {/* Prompts grid */}
          {filteredPrompts.length === 0 ? (
            <Box textAlign="center" py={12}>
              <VStack gap={4}>
                <Text fontSize="lg" color="gray.500">
                  {searchQuery
                    ? 'No prompts found matching your search.'
                    : 'No prompts yet. Create your first prompt to get started!'
                  }
                </Text>
                {/* Empty state - user can click the "New Prompt" button in the header */}
              </VStack>
            </Box>
          ) : (
            <Grid
              templateColumns={{
                base: '1fr',
                md: 'repeat(2, 1fr)',
                lg: 'repeat(3, 1fr)',
              }}
              gap={6}
            >
              {filteredPrompts.map((prompt) => (
                <PromptCard
                  key={`${prompt.repo_name}:${prompt.file_path}`}
                  prompt={prompt}
                  onEdit={handleEditPrompt}
                  onDelete={handleDeletePrompt}
                />
              ))}
            </Grid>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <Pagination
              currentPage={currentPage}
              totalPages={totalPages}
              onPageChange={setPage}
              totalItems={totalPrompts}
              itemsPerPage={itemsPerPage}
            />
          )}
                </VStack>
              </Container>
            </Box>
          </ScrollArea.Content>
        </ScrollArea.Viewport>
        <ScrollArea.Scrollbar orientation="vertical">
          <ScrollArea.Thumb />
        </ScrollArea.Scrollbar>
        </ScrollArea.Root>

        {/* Delete Confirmation Dialog */}
        <DeletePromptDialog
          open={deleteDialogOpen}
          onOpenChange={closeDeleteDialog}
          promptName={promptToDelete?.name || 'this prompt'}
          onConfirm={confirmDelete}
          isDeleting={isDeleting}
        />
      </Box>
  );
}