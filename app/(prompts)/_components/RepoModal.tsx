"use client"

import React from "react";
import {
  Box,
  Button,
  HStack,
  VStack,
  Text,
} from '@chakra-ui/react';
import Repos, { SelectedRepo } from './Repos';

interface RepoModalProps {
  isOpen: boolean;
  onClose: () => void;
  isLoggedIn: boolean;
  handleGitHubLogin: () => void;
  selectedRepo: string;
  setSelectedRepo: (id: string) => void;
  selectedBranch: string;
  setSelectedBranch: (branch: string) => void;
  selectedRepos: Array<SelectedRepo>;
  toggleRepoSelection: (id: number, branch: string, name: string) => void;
}

export function RepoModal({
  isOpen,
  onClose,
  isLoggedIn,
  handleGitHubLogin,
  selectedRepo,
  setSelectedRepo,
  selectedBranch,
  setSelectedBranch,
  selectedRepos,
  toggleRepoSelection
}: RepoModalProps) {
  if (!isOpen) return null;

  return (
    <Box
      position="fixed"
      top="0"
      left="0"
      right="0"
      bottom="0"
      bg="blackAlpha.600"
      zIndex="1000"
      display="flex"
      alignItems="center"
      justifyContent="center"
      onClick={onClose}
    >
      <Box
        bg="white"
        borderRadius="lg"
        boxShadow="xl"
        maxW="4xl"
        w="90%"
        maxH="90vh"
        overflow="auto"
        onClick={(e) => e.stopPropagation()}
        _dark={{ bg: "gray.800" }}
      >
        <VStack gap={0} align="stretch">
          <Box p={6} borderBottom="1px solid" borderColor="border.muted">
            <HStack justify="space-between" align="center">
              <VStack align="start" gap={1}>
                <Text fontSize="xl" fontWeight="bold">
                  Configure Prompt Repositories
                </Text>
                <Text fontSize="sm" opacity={0.7}>
                  Select repositories to associate with your prompts
                </Text>
              </VStack>
              <Button
                variant="ghost"
                size="sm"
                onClick={onClose}
              >
                ✕
              </Button>
            </HStack>
          </Box>
          
          <Box p={6}>
            <Repos
              isLoggedIn={isLoggedIn}
              handleGitHubLogin={handleGitHubLogin}
              selectedRepo={selectedRepo}
              setSelectedRepo={setSelectedRepo}
              selectedBranch={selectedBranch}
              setSelectedBranch={setSelectedBranch}
              selectedRepos={selectedRepos}
              toggleRepoSelection={toggleRepoSelection}
            />
          </Box>
          
          <Box p={6} borderTop="1px solid" borderColor="border.muted">
            <HStack justify="flex-end" gap={3}>
              <Button variant="outline" onClick={onClose}>
                Cancel
              </Button>
              <Button colorPalette="blue" onClick={onClose}>
                Done
              </Button>
            </HStack>
          </Box>
        </VStack>
      </Box>
    </Box>
  );
}