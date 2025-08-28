'use client';

import React from 'react';
import {
  Box,
  Container,
  VStack,
  HStack,
  Text,
  Button,
} from '@chakra-ui/react';
import { LuPlus, LuFolderGit } from 'react-icons/lu';
import { useColorModeValue } from '@/components/ui/color-mode';

interface PromptsHeaderProps {
  onCreateNew: () => void;
  onAddRepoClick: () => void;
}

export function PromptsHeader({ onCreateNew, onAddRepoClick }: PromptsHeaderProps) {
  const headerBg = useColorModeValue('gray.50', 'gray.900');

  return (
    <Box
      bg={headerBg}
      borderBottom="1px solid"
      borderColor="border.muted"
      py={4}
      position="sticky"
      top={0}
      zIndex={10}
    >
      <Container maxW="7xl" mx="auto">
        <HStack justify="space-between" align="center">
          <VStack align="start" gap={1}>
            <Text fontSize="2xl" fontWeight="bold">
              Prompts
            </Text>
            <Text fontSize="sm" opacity={0.7}>
              Manage and organize your AI prompts
            </Text>
          </VStack>
          <HStack gap={3}>
            <Button
              onClick={onAddRepoClick}
              variant="outline"
              colorPalette="gray"
            >
              <HStack gap={2}>
                <LuFolderGit size={16} />
                <Text>Add Prompt Repo</Text>
              </HStack>
            </Button>
            <Button
              onClick={onCreateNew}
              colorPalette="blue"
            >
              <HStack gap={2}>
                <LuPlus size={16} />
                <Text>New Prompt</Text>
              </HStack>
            </Button>
          </HStack>
        </HStack>
      </Container>
    </Box>
  );
}