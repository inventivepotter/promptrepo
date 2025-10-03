'use client';

import React, { useState } from 'react';
import {
  Box,
  Container,
  HStack,
  VStack,
  Text,
  Button,
} from '@chakra-ui/react';
import { LuPlus } from 'react-icons/lu';
import { CreatePromptModal } from './CreatePromptModal';

interface PromptsHeaderProps {
  onCreateNew?: () => void;
}

export function PromptsHeader({ onCreateNew }: PromptsHeaderProps) {
  const headerBg = "bg.subtle";
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleCreateClick = () => {
    if (onCreateNew) {
      onCreateNew();
    } else {
      setIsModalOpen(true);
    }
  };

  return (
    <>
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
            
            <HStack gap={3}>
              <Button variant="solid" onClick={handleCreateClick}>
                <LuPlus /> New Prompt
              </Button>
            </HStack>
          </HStack>
        </Container>
      </Box>
      
      <CreatePromptModal open={isModalOpen} onOpenChange={setIsModalOpen} />
    </>
  );
}