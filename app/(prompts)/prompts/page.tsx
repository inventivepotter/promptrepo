'use client';

import { useRouter } from 'next/navigation';
import {
  Box,
  VStack,
  HStack,
  Text,
  Button,
  Grid,
  Container,
} from '@chakra-ui/react';
import { LuPlus } from 'react-icons/lu';
import { useColorModeValue } from '../../../components/ui/color-mode';
import { usePromptsState, Prompt } from '../_state/promptState';
import { PromptSearch } from '../_components/PromptSearch';
import { PromptCard } from '../_components/PromptCard';
import { Pagination } from '../_components/Pagination';

export default function PromptsPage() {
  const router = useRouter();
  
  // Theme-aware colors
  const headerBg = useColorModeValue('white', 'gray.900');
  const containerBg = useColorModeValue('gray.50', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

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
  } = usePromptsState();


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
    <Box minH="100vh" bg={containerBg}>
      {/* Header */}
      <Box
        bg={headerBg}
        borderBottom="1px solid"
        borderColor={borderColor}
        py={4}
        position="sticky"
        top={0}
        zIndex={10}
      >
        <Container maxW="7xl">
          <HStack justify="space-between" align="center">
            <VStack align="start" gap={1}>
              <Text fontSize="2xl" fontWeight="bold">
                Prompts
              </Text>
              <Text fontSize="sm" opacity={0.7}>
                Manage and organize your AI prompts
              </Text>
            </VStack>
            <Button
              onClick={handleCreateNew}
              colorPalette="blue"
            >
              <HStack gap={2}>
                <LuPlus size={16} />
                <Text>New Prompt</Text>
              </HStack>
            </Button>
          </HStack>
        </Container>
      </Box>

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
    </Box>
  );
}