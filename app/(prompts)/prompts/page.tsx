'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import {
  VStack,
  HStack,
  Text,
  Button,
  Grid,
  Box,
  Container,
} from '@chakra-ui/react';
import { LuPlus } from 'react-icons/lu';
import { Prompt } from '@/types/Prompt';
import { usePromptsState } from '../_state/promptState';
import { PromptSearch } from '../_components/PromptSearch';
import { PromptCard } from '../_components/PromptCard';
import { Pagination } from '../_components/Pagination';
import { RepoModal } from '../_components/RepoModal';
import { PromptsHeader } from '@/components/PromptsHeader';

export default function PromptsPage() {
  const router = useRouter();
  const [isRepoModalOpen, setIsRepoModalOpen] = React.useState(false);

  const {
    filteredPrompts,
    totalPrompts,
    totalPages,
    promptsState,
    createPrompt,
    deletePrompt,
    setCurrentPrompt,
    setSearchQuery,
    setCurrentPage,
    setSortBy,
    setRepoFilter,
    updateCurrentRepoStepField,
    toggleRepoSelection,
    handleGitHubLogin,
  } = usePromptsState();

  // Get available repositories from prompts
  const availableRepos = React.useMemo(() => {
    const repos = new Set<string>();
    promptsState.prompts.forEach(prompt => {
      if (prompt.repo?.name) {
        repos.add(prompt.repo.name);
      }
    });
    return Array.from(repos).sort();
  }, [promptsState.prompts]);


  const handleCreateNew = () => {
    const newPrompt = createPrompt();
    router.push(`/editor?id=${newPrompt.id}`);
  };

  const handleEditPrompt = (prompt: Prompt) => {
    setCurrentPrompt(prompt);
    router.push(`/editor?id=${prompt.id}`);
  };

  const handleDeletePrompt = (id: string) => {
    if (confirm('Are you sure you want to delete this prompt?')) {
      deletePrompt(id);
    }
  };

  return (
    <VStack minH="100vh" align="stretch">
      <PromptsHeader
        onCreateNew={handleCreateNew}
        onAddRepoClick={() => setIsRepoModalOpen(true)}
      />
      {/* Main content */}
      <Container maxW="7xl" py={6}>
        <VStack gap={6} align="stretch">
          {/* Search and filters */}
          <PromptSearch
            searchQuery={promptsState.searchQuery}
            onSearchChange={setSearchQuery}
            sortBy={promptsState.sortBy}
            sortOrder={promptsState.sortOrder}
            onSortChange={setSortBy}
            totalPrompts={totalPrompts}
            repoFilter={promptsState.repoFilter}
            onRepoFilterChange={setRepoFilter}
            availableRepos={availableRepos}
          />

          {/* Prompts grid */}
          {filteredPrompts.length === 0 ? (
            <Box textAlign="center" py={12}>
              <VStack gap={4}>
                <Text fontSize="lg" color="gray.500">
                  {promptsState.searchQuery
                    ? 'No prompts found matching your search.'
                    : 'No prompts yet. Create your first prompt to get started!'
                  }
                </Text>
                {!promptsState.searchQuery && (
                  <Button
                    onClick={handleCreateNew}
                    colorPalette="blue"
                  >
                    <HStack gap={2}>
                      <LuPlus size={16} />
                      <Text>Create First Prompt</Text>
                    </HStack>
                  </Button>
                )}
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
                  key={prompt.id}
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
              currentPage={promptsState.currentPage}
              totalPages={totalPages}
              onPageChange={setCurrentPage}
              totalItems={totalPrompts}
              itemsPerPage={promptsState.itemsPerPage}
            />
          )}
        </VStack>
      </Container>

      {/* Repo Configuration Modal */}
      <RepoModal
        isOpen={isRepoModalOpen}
        onClose={() => setIsRepoModalOpen(false)}
        isLoggedIn={promptsState.currentRepoStep.isLoggedIn}
        handleGitHubLogin={handleGitHubLogin}
        selectedRepo={promptsState.currentRepoStep.selectedRepo}
        setSelectedRepo={(repo: string) => updateCurrentRepoStepField('selectedRepo', repo)}
        selectedBranch={promptsState.currentRepoStep.selectedBranch}
        setSelectedBranch={(branch: string) => updateCurrentRepoStepField('selectedBranch', branch)}
        configuredRepos={promptsState.configuredRepos}
        toggleRepoSelection={toggleRepoSelection}
      />
    </VStack>
  );
}