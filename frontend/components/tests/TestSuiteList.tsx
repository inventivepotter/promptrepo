'use client';

import React, { useState } from 'react';
import { Box, VStack, Text, Button, HStack, Input, SimpleGrid } from '@chakra-ui/react';
import { LuPlus } from 'react-icons/lu';
import { TestSuiteCard } from './TestSuiteCard';
import { DeletePromptDialog } from '../DeletePromptDialog';
import { useTestStore } from '@/stores/testStore';
import type { TestSuiteSummary } from '@/types/test';

interface TestSuiteListProps {
  repoName: string;
  onCreateNew: () => void;
  onViewSuite: (suiteName: string) => void;
}

export function TestSuiteList({ repoName, onCreateNew, onViewSuite }: TestSuiteListProps) {
  const testSuites = useTestStore((state) => state.testSuites);
  const deleteTestSuite = useTestStore((state) => state.deleteTestSuite);
  const isLoading = useTestStore((state) => state.isLoading);
  
  const [searchQuery, setSearchQuery] = useState('');
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [suiteToDelete, setSuiteToDelete] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  // Filter test suites based on search query
  const filteredSuites = testSuites.filter((suite) => {
    const query = searchQuery.toLowerCase();
    return (
      suite.name.toLowerCase().includes(query) ||
      suite.description.toLowerCase().includes(query) ||
      suite.tags.some((tag) => tag.toLowerCase().includes(query))
    );
  });

  const handleDeleteClick = (suiteName: string) => {
    setSuiteToDelete(suiteName);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!suiteToDelete) return;
    
    setIsDeleting(true);
    try {
      await deleteTestSuite(repoName, suiteToDelete);
      setDeleteDialogOpen(false);
      setSuiteToDelete(null);
    } catch (error) {
      console.error('Failed to delete test suite:', error);
    } finally {
      setIsDeleting(false);
    }
  };

  if (isLoading) {
    return (
      <Box p={6} textAlign="center">
        <Text>Loading test suites...</Text>
      </Box>
    );
  }

  return (
    <Box>
      <VStack align="stretch" gap={4}>
        <HStack justify="space-between">
          <Input
            placeholder="Search test suites..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            maxW="400px"
          />
          <Button onClick={onCreateNew}>
            <LuPlus /> Create Test Suite
          </Button>
        </HStack>

        {filteredSuites.length === 0 ? (
          <Box
            p={8}
            textAlign="center"
            border="1px dashed"
            borderColor="gray.300"
            borderRadius="md"
          >
            <Text fontSize="lg" color="gray.600" mb={2}>
              {testSuites.length === 0
                ? 'No test suites yet'
                : 'No test suites match your search'}
            </Text>
            {testSuites.length === 0 && (
              <Text fontSize="sm" color="gray.500" mb={4}>
                Create your first test suite to get started
              </Text>
            )}
            {testSuites.length === 0 && (
              <Button onClick={onCreateNew} variant="outline">
                <LuPlus /> Create Test Suite
              </Button>
            )}
          </Box>
        ) : (
          <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} gap={4}>
            {filteredSuites.map((suite) => (
              <TestSuiteCard
                key={suite.name}
                suite={suite}
                onView={onViewSuite}
                onDelete={handleDeleteClick}
              />
            ))}
          </SimpleGrid>
        )}
      </VStack>

      <DeletePromptDialog
        open={deleteDialogOpen}
        onOpenChange={setDeleteDialogOpen}
        promptName={suiteToDelete || ''}
        onConfirm={handleDeleteConfirm}
        isDeleting={isDeleting}
      />
    </Box>
  );
}