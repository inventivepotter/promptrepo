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
import { useColorModeValue } from '../../../components/ui/color-mode';

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
  // Theme-aware colors
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const mutedTextColor = useColorModeValue('gray.600', 'gray.400');
  const activeBg = useColorModeValue('blue.50', 'blue.900');
  const activeColor = useColorModeValue('blue.600', 'blue.300');
  const hoverBg = useColorModeValue('gray.50', 'gray.700');

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
    <VStack gap={4} align="stretch" mb={6}>
      <HStack justify="space-between" align="start" flexWrap="wrap" gap={4}>
        <Box flex={1} maxW="400px" position="relative">
          <Input
            placeholder="Search prompts by name or description..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            borderColor={borderColor}
            paddingRight="2.5rem"
            _focus={{
              borderColor: activeColor,
              boxShadow: `0 0 0 1px ${activeColor}`,
            }}
          />
          <Box
            position="absolute"
            right="0.75rem"
            top="50%"
            transform="translateY(-50%)"
            pointerEvents="none"
          >
            <LuSearch size={16} color={mutedTextColor} />
          </Box>
        </Box>

        <HStack gap={2} align="center">
          <Text fontSize="sm" color={mutedTextColor}>
            Sort by:
          </Text>
          <Button
            size="sm"
            variant={sortBy === 'name' ? 'solid' : 'ghost'}
            onClick={() => handleSortToggle('name')}
            bg={sortBy === 'name' ? activeBg : 'transparent'}
            color={sortBy === 'name' ? activeColor : mutedTextColor}
            _hover={{ bg: sortBy === 'name' ? activeBg : hoverBg }}
          >
            <HStack gap={1}>
              <Text>Name</Text>
              {sortBy === 'name' && (
                sortOrder === 'asc' ? (
                  <LuArrowUp size={12} />
                ) : (
                  <LuArrowDown size={12} />
                )
              )}
            </HStack>
          </Button>
          <Button
            size="sm"
            variant={sortBy === 'updated_at' ? 'solid' : 'ghost'}
            onClick={() => handleSortToggle('updated_at')}
            bg={sortBy === 'updated_at' ? activeBg : 'transparent'}
            color={sortBy === 'updated_at' ? activeColor : mutedTextColor}
            _hover={{ bg: sortBy === 'updated_at' ? activeBg : hoverBg }}
          >
            <HStack gap={1}>
              <Text>Last Updated</Text>
              {sortBy === 'updated_at' && (
                sortOrder === 'asc' ? (
                  <LuArrowUp size={12} />
                ) : (
                  <LuArrowDown size={12} />
                )
              )}
            </HStack>
          </Button>
        </HStack>
      </HStack>

      <Text fontSize="sm" color={mutedTextColor}>
        {totalPrompts} prompt{totalPrompts !== 1 ? 's' : ''} found
      </Text>
    </VStack>
  );
}