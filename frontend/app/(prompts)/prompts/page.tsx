'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  VStack,
  Text,
  Grid,
  Box,
  Container,
  ScrollArea,
  SkeletonText,
  EmptyState,
  Button,
  ButtonGroup,
} from '@chakra-ui/react';
import { HiColorSwatch } from 'react-icons/hi';
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
  useIsLoading,
} from '@/stores/promptStore';
import { PromptSearch } from '../_components/PromptSearch';
import { PromptCard } from '../_components/PromptCard';
import { Pagination } from '../_components/Pagination';
import { PromptsHeader } from '@/components/PromptsHeader';
import { DeletePromptDialog } from '@/components/DeletePromptDialog';
import { CreatePromptModal } from '@/components/CreatePromptModal';

export default function PromptsPage() {
  const router = useRouter();
  const [isNewPromptModalOpen, setIsNewPromptModalOpen] = useState(false);
  
  // Use prompt store hooks
  const isLoading = useIsLoading();
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
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Empty dependency array ensures this runs only once on mount

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

  const handleAddRepositories = () => {
    router.push('/config#repositories');
  };

  const handleNewPrompt = () => {
    setIsNewPromptModalOpen(true);
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
          {isLoading ? (
            <Grid
              templateColumns={{
                base: '1fr',
                md: 'repeat(2, 1fr)',
                lg: 'repeat(3, 1fr)',
              }}
              gap={6}
            >
              {[...Array(6)].map((_, index) => (
                <Box
                  key={index}
                  p={6}
                  borderRadius="md"
                  bg="bg.subtle"
                  borderWidth="1px"
                  borderColor="transparent"
                  minHeight="200px"
                >
                  <SkeletonText
                    noOfLines={3}
                    gap={5}
                    height={5}
                    opacity={0.2}
                  />
                </Box>
              ))}
            </Grid>
          ) : filteredPrompts.length === 0 ? (
            searchQuery ? (
              <Box textAlign="center" py={12}>
                <VStack gap={4}>
                  <Text fontSize="lg" color="gray.500">
                    No prompts found matching your search.
                  </Text>
                </VStack>
              </Box>
            ) : (
              <EmptyState.Root>
                <EmptyState.Content>
                  <EmptyState.Indicator>
                    <HiColorSwatch />
                  </EmptyState.Indicator>
                  <VStack textAlign="center">
                    <EmptyState.Title>Start adding prompts</EmptyState.Title>
                    <EmptyState.Description>
                      Add repositories or create a new prompt to get started
                    </EmptyState.Description>
                  </VStack>
                  <ButtonGroup>
                    <Button onClick={handleAddRepositories}>Add Repositories</Button>
                    <Button variant="outline" onClick={handleNewPrompt}>New Prompt</Button>
                  </ButtonGroup>
                </EmptyState.Content>
              </EmptyState.Root>
            )
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

        {/* Create Prompt Modal */}
        <CreatePromptModal
          open={isNewPromptModalOpen}
          onOpenChange={setIsNewPromptModalOpen}
        />
      </Box>
  );
}