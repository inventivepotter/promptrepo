'use client';

import React, { useState } from 'react';
import { Box, VStack, Text, Button, HStack, Input, SimpleGrid } from '@chakra-ui/react';
import { LuPlus } from 'react-icons/lu';
import { EvalCard } from './EvalCard';
import { DeletePromptDialog } from '../DeletePromptDialog';
import { useEvalStore } from '@/stores/evalStore';
import type { EvalSummary } from '@/types/eval';

interface EvalListProps {
  repoName: string;
  onCreateNew: () => void;
  onViewEval: (evalName: string) => void;
}

export function EvalList({ repoName, onCreateNew, onViewEval }: EvalListProps) {
  const evals = useEvalStore((state) => state.evals);
  const deleteEval = useEvalStore((state) => state.deleteEval);
  const isLoading = useEvalStore((state) => state.isLoading);
  
  const [searchQuery, setSearchQuery] = useState('');
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [evalToDelete, setEvalToDelete] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  // Filter evals based on search query
  const filteredEvals = evals.filter((evalData) => {
    const query = searchQuery.toLowerCase();
    return (
      evalData.name.toLowerCase().includes(query) ||
      evalData.description.toLowerCase().includes(query) ||
      evalData.tags.some((tag) => tag.toLowerCase().includes(query))
    );
  });

  const handleDeleteClick = (evalName: string) => {
    setEvalToDelete(evalName);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!evalToDelete) return;
    
    setIsDeleting(true);
    try {
      await deleteEval(repoName, evalToDelete);
      setDeleteDialogOpen(false);
      setEvalToDelete(null);
    } catch (error) {
      console.error('Failed to delete eval:', error);
    } finally {
      setIsDeleting(false);
    }
  };

  if (isLoading) {
    return (
      <Box p={6} textAlign="center">
        <Text>Loading evals...</Text>
      </Box>
    );
  }

  return (
    <Box>
      <VStack align="stretch" gap={4}>
        <HStack justify="space-between">
          <Input
            placeholder="Search evals..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            maxW="400px"
          />
          <Button onClick={onCreateNew}>
            <LuPlus /> Create Eval
          </Button>
        </HStack>

        {filteredEvals.length === 0 ? (
          <Box
            p={8}
            textAlign="center"
            border="1px dashed"
            borderColor="gray.300"
            borderRadius="md"
          >
            <Text fontSize="lg" color="gray.600" mb={2}>
              {evals.length === 0
                ? 'No evals yet'
                : 'No evals match your search'}
            </Text>
            {evals.length === 0 && (
              <Text fontSize="sm" color="gray.500" mb={4}>
                Create your first eval to get started
              </Text>
            )}
            {evals.length === 0 && (
              <Button onClick={onCreateNew} variant="outline">
                <LuPlus /> Create Eval
              </Button>
            )}
          </Box>
        ) : (
          <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} gap={4}>
            {filteredEvals.map((evalData) => (
              <EvalCard
                key={evalData.name}
                eval={evalData}
                onView={onViewEval}
                onDelete={handleDeleteClick}
              />
            ))}
          </SimpleGrid>
        )}
      </VStack>

      <DeletePromptDialog
        open={deleteDialogOpen}
        onOpenChange={setDeleteDialogOpen}
        promptName={evalToDelete || ''}
        onConfirm={handleDeleteConfirm}
        isDeleting={isDeleting}
      />
    </Box>
  );
}