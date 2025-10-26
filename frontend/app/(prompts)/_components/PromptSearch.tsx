'use client';

import React from 'react';
import {
  Box,
  HStack,
  VStack,
  Text,
  Button,
  Input,
} from '@chakra-ui/react';
import { LuSearch, LuArrowUp, LuArrowDown } from 'react-icons/lu';
import { useSelectedRepository } from '@/stores/repositoryFilterStore';

interface PromptSearchProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
  sortBy: 'name' | 'updated_at';
  sortOrder: 'asc' | 'desc';
  onSortChange: (sortBy: 'name' | 'updated_at', sortOrder: 'asc' | 'desc') => void;
  totalPrompts: number;
}

export function PromptSearch({
  searchQuery,
  onSearchChange,
  sortBy,
  sortOrder,
  onSortChange,
  totalPrompts,
}: PromptSearchProps) {
  // Get repository filter from shared store for display purposes
  const selectedRepository = useSelectedRepository();

  const handleSortToggle = (field: 'name' | 'updated_at') => {
    if (sortBy === field) {
      // Toggle order if same field
      onSortChange(field, sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      // Default to desc for new field
      onSortChange(field, field === 'updated_at' ? 'desc' : 'asc');
    }
  };

  return (
    <Box
      p={6}
      borderWidth="1px"
      borderRadius="lg"
      borderColor="bg.muted"
      bg="bg.subtle"
      shadow="sm"
      _hover={{ shadow: "md" }}
      transition="all 0.2s"
    >
      <VStack gap={4} align="stretch" mb={0}>
        <HStack justify="space-between" align="center" flexWrap="wrap" gap={4}>
          <Box flex={1} maxW="400px" position="relative" height="40px">
            <Input
              placeholder="Search prompts by name or description..."
              value={searchQuery}
              onChange={(e) => onSearchChange(e.target.value)}
              paddingRight="2.5rem"
              size="md"
              height="100%"
              borderRadius="md"
              borderColor="bg.muted"
              bg="bg"
              _hover={{ borderColor: "bg.muted" }}
              _focus={{
                borderColor: "colorPalette.500",
                boxShadow: "0 0 0 1px var(--chakra-colors-colorPalette-500)"
              }}
              transition="all 0.2s"
            />
            <Box
              position="absolute"
              right="0.75rem"
              top="50%"
              transform="translateY(-50%)"
              pointerEvents="none"
              color="fg.muted"
            >
              <LuSearch size={18} />
            </Box>
          </Box>

          <HStack
            gap={2}
            align="center"
            px={3}
            height="40px"
            borderRadius="md"
            bg="bg"
            borderWidth="1px"
            borderColor="bg.muted"
          >
            <Text fontSize="sm" fontWeight="medium" color="fg.muted">
              Sort by:
            </Text>
            <Button
              size="sm"
              variant={sortBy === 'name' ? 'solid' : 'ghost'}
              onClick={() => handleSortToggle('name')}
              bg={sortBy === 'name' ? "primary.muted" : 'transparent'}
              color={sortBy === 'name' ? "primary.solid" : "fg"}
              _hover={{
                bg: sortBy === 'name' ? "primary.subtle" : "bg.muted",
                transform: "translateY(-1px)",
                borderRadius: sortBy === 'name' ? "0 !important" : "md"
              }}
              _active={{ transform: "translateY(0)" }}
              borderRadius={sortBy === 'name' ? "0" : "md"}
              transition="all 0.2s"
            >
              <HStack gap={1}>
                <Text fontWeight={sortBy === 'name' ? "semibold" : "normal"}>Name</Text>
                {sortBy === 'name' && (
                  sortOrder === 'asc' ? (
                    <LuArrowUp size={14} />
                  ) : (
                    <LuArrowDown size={14} />
                  )
                )}
              </HStack>
            </Button>
            <Button
              size="sm"
              variant={sortBy === 'updated_at' ? 'solid' : 'ghost'}
              onClick={() => handleSortToggle('updated_at')}
              bg={sortBy === 'updated_at' ? "primary.muted" : 'transparent'}
              color={sortBy === 'updated_at' ? "primary.solid" : "fg"}
              _hover={{
                bg: sortBy === 'updated_at' ? "primary.subtle" : "bg.muted",
                transform: "translateY(-1px)",
                borderRadius: sortBy === 'updated_at' ? "0 !important" : "md"
              }}
              _active={{ transform: "translateY(0)" }}
              borderRadius={sortBy === 'updated_at' ? "0" : "md"}
              transition="all 0.2s"
            >
              <HStack gap={1}>
                <Text fontWeight={sortBy === 'updated_at' ? "semibold" : "normal"}>Last Updated</Text>
                {sortBy === 'updated_at' && (
                  sortOrder === 'asc' ? (
                    <LuArrowUp size={14} />
                  ) : (
                    <LuArrowDown size={14} />
                  )
                )}
              </HStack>
            </Button>
          </HStack>
        </HStack>

        <HStack justify="space-between" pt={2} borderTopWidth="1px" borderColor="bg.muted">
          <Text fontSize="sm" fontWeight="medium" color="fg.muted">
            {totalPrompts} prompt{totalPrompts !== 1 ? 's' : ''} found
          </Text>
          {selectedRepository && (
            <HStack gap={2}>
              <Text fontSize="sm" color="fg.muted">Repository:</Text>
              <Text
                fontSize="sm"
                fontWeight="semibold"
                color="fg.muted"
              >
                {selectedRepository}
              </Text>
            </HStack>
          )}
        </HStack>
      </VStack>
    </Box>
  );
}