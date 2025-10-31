'use client';

import React, { useState } from 'react';
import { Box, VStack, Text, Button, HStack, Input, SimpleGrid } from '@chakra-ui/react';
import { LuPlus } from 'react-icons/lu';
import { EvalSuiteCard } from './EvalSuiteCard';
import { DeletePromptDialog } from '../DeletePromptDialog';
import { useEvalStore } from '@/stores/evalStore';
import type { EvalSuiteSummary } from '@/types/eval';

interface EvalSuiteListProps {
  repoName: string;
  onCreateNew: () => void;
  onViewSuite: (suiteName: string) => void;
}

export function EvalSuiteList({ repoName, onCreateNew, onViewSuite }: EvalSuiteListProps) {
  const evalSuites = useEvalStore((state) => state.evalSuites);
  const deleteEvalSuite = useEvalStore((state) => state.deleteEvalSuite);
  const isLoading = useEvalStore((state) => state.isLoading);
  
  const [searchQuery, setSearchQuery] = useState('');
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [suiteToDelete, setSuiteToDelete] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  // Filter eval suites based on search query
  const filteredSuites = evalSuites.filter((suite) => {
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
      await deleteEvalSuite(repoName, suiteToDelete);
      setDeleteDialogOpen(false);
      setSuiteToDelete(null);
    } catch (error) {
      console.error('Failed to delete eval suite:', error);
    } finally {
      setIsDeleting(false);
    }
  };

  if (isLoading) {
    return (
      <Box p={6} textAlign="center">
        <Text>Loading eval suites...</Text>
      </Box>
    );
  }

  return (
    <Box>
      <VStack align="stretch" gap={4}>
        <HStack justify="space-between">
          <Input
            placeholder="Search eval suites..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            maxW="400px"
          />
          <Button onClick={onCreateNew}>
            <LuPlus /> Create Eval Suite
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
              {evalSuites.length === 0
                ? 'No eval suites yet'
                : 'No eval suites match your search'}
            </Text>
            {evalSuites.length === 0 && (
              <Text fontSize="sm" color="gray.500" mb={4}>
                Create your first eval suite to get started
              </Text>
            )}
            {evalSuites.length === 0 && (
              <Button onClick={onCreateNew} variant="outline">
                <LuPlus /> Create Eval Suite
              </Button>
            )}
          </Box>
        ) : (
          <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} gap={4}>
            {filteredSuites.map((suite) => (
              <EvalSuiteCard
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