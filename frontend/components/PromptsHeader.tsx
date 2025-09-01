'use client';

import React from 'react';
import {
  Box,
  Container,
  HStack,
  VStack,
  Text,
  Button,
} from '@chakra-ui/react';
import { LuPlus, LuGitBranch } from 'react-icons/lu';
import { useColorModeValue } from '@/components/ui/color-mode';

interface PromptsHeaderProps {
  onCreateNew: () => void;
  onCommitPush?: () => void;
}

export function PromptsHeader({ onCreateNew, onCommitPush }: PromptsHeaderProps) {
  const headerBg = useColorModeValue('gray.50', 'gray.900');
  const mutedTextColor = useColorModeValue('gray.600', 'gray.400');

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
            <Text fontSize="sm" color={mutedTextColor}>
              Create and manage your AI prompts with version control
            </Text>
          </VStack>
          
          <HStack gap={3}>
            <Button
              onClick={onCreateNew}
              colorPalette="blue"
            >
              <HStack gap={2}>
                <LuPlus size={16} />
                <Text>New Prompt</Text>
              </HStack>
            </Button>
            
            <Button
              onClick={onCommitPush}
              colorPalette="green"
              variant="outline"
            >
              <HStack gap={2}>
                <LuGitBranch size={16} />
                <Text>Commit & Push</Text>
              </HStack>
            </Button>
          </HStack>
        </HStack>
      </Container>
    </Box>
  );
}