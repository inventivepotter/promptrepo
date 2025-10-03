'use client';

import React from 'react';
import {
  Box,
  HStack,
  VStack,
  Text,
  Button,
  Input,
  Combobox,
  createListCollection,
} from '@chakra-ui/react';
import { LuSearch, LuArrowUp, LuArrowDown } from 'react-icons/lu';
import { FaChevronDown } from 'react-icons/fa';
import { useColorModeValue } from '@/components/ui/color-mode';

interface PromptSearchProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
  sortBy: 'name' | 'updated_at';
  sortOrder: 'asc' | 'desc';
  onSortChange: (sortBy: 'name' | 'updated_at', sortOrder: 'asc' | 'desc') => void;
  totalPrompts: number;
  repoFilter: string;
  onRepoFilterChange: (repo: string) => void;
  availableRepos: string[];
}

export function PromptSearch({
  searchQuery,
  onSearchChange,
  sortBy,
  sortOrder,
  onSortChange,
  totalPrompts,
  repoFilter,
  onRepoFilterChange,
  availableRepos,
}: PromptSearchProps) {
  const [repoSearchValue, setRepoSearchValue] = React.useState('');

  // Theme-aware colors
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const mutedTextColor = useColorModeValue('gray.600', 'gray.400');
  const activeBg = useColorModeValue('blue.50', 'blue.900');
  const activeColor = useColorModeValue('blue.600', 'blue.300');
  const hoverBg = useColorModeValue('gray.50', 'gray.700');

  // Filter repositories based on search value
  const filteredRepos = availableRepos.filter(repo =>
    repo.toLowerCase().includes(repoSearchValue.toLowerCase())
  );

  // Create filtered collection for combobox
  const repoCollection = [
    { label: 'All Repositories', value: '' },
    ...filteredRepos.map(repo => ({ label: repo, value: repo }))
  ];

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
    <Box p={6} borderWidth="1px" borderRadius="md" borderColor="border.emphasized">
      <VStack gap={4} align="stretch" mb={0}>
        <HStack justify="space-between" align="start" flexWrap="wrap" gap={4}>
          <HStack gap={4} flex={1}>
            <Box flex={1} maxW="400px" position="relative">
              <Input
                placeholder="Search prompts by name, description, or repo..."
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
            
            {availableRepos.length > 0 && (
              <Box minW="200px">
                <Combobox.Root
                  collection={createListCollection({
                    items: repoCollection
                  })}
                  value={[repoFilter]}
                  onValueChange={(e) => onRepoFilterChange(e.value[0] || '')}
                  inputValue={repoSearchValue}
                  onInputValueChange={(e) => setRepoSearchValue(e.inputValue)}
                  openOnClick
                >
                  <Combobox.Control position="relative">
                    <Combobox.Input
                      placeholder="Filter by repository"
                      paddingRight="2rem"
                      borderColor={borderColor}
                      _focus={{
                        borderColor: activeColor,
                        boxShadow: `0 0 0 1px ${activeColor}`,
                      }}
                    />
                    <Combobox.Trigger position="absolute" right="0.5rem" top="50%" transform="translateY(-50%)">
                      <FaChevronDown size={16} />
                    </Combobox.Trigger>
                  </Combobox.Control>
                  <Combobox.Positioner>
                    <Combobox.Content>
                      <Combobox.Item key="all" item="">
                        <Combobox.ItemText>All Repositories</Combobox.ItemText>
                        <Combobox.ItemIndicator />
                      </Combobox.Item>
                      {filteredRepos.map(repo => (
                        <Combobox.Item key={repo} item={repo}>
                          <Combobox.ItemText>{repo}</Combobox.ItemText>
                          <Combobox.ItemIndicator />
                        </Combobox.Item>
                      ))}
                    </Combobox.Content>
                  </Combobox.Positioner>
                </Combobox.Root>
              </Box>
            )}
          </HStack>

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

        <HStack justify="space-between">
          <Text fontSize="sm" color={mutedTextColor}>
            {totalPrompts} prompt{totalPrompts !== 1 ? 's' : ''} found
          </Text>
          {repoFilter && (
            <Text fontSize="sm" color={activeColor}>
              Filtered by: {repoFilter}
            </Text>
          )}
        </HStack>
      </VStack>
    </Box>
  );
}