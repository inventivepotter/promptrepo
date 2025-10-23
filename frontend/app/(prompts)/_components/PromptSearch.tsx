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
    <Box
      p={6}
      borderWidth="1px"
      borderRadius="lg"
      borderColor="border.emphasized"
      bg="bg.subtle"
      shadow="sm"
      _hover={{ shadow: "md" }}
      transition="all 0.2s"
    >
      <VStack gap={4} align="stretch" mb={0}>
        <HStack justify="space-between" align="center" flexWrap="wrap" gap={4}>
          <HStack gap={4} flex={1} height="40px">
            <Box flex={1} maxW="400px" position="relative" height="100%">
              <Input
                placeholder="Search prompts by name, description, or repo..."
                value={searchQuery}
                onChange={(e) => onSearchChange(e.target.value)}
                paddingRight="2.5rem"
                size="md"
                height="100%"
                borderRadius="md"
                borderColor="border"
                bg="bg"
                _hover={{ borderColor: "border.emphasized" }}
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
            
            {availableRepos.length > 0 && (
              <Box minW="200px" height="100%">
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
                  <Combobox.Control position="relative" height="100%">
                    <Combobox.Input
                      placeholder="Filter by repository"
                      paddingRight="2rem"
                      height="100%"
                      borderRadius="md"
                      borderColor="border"
                      bg="bg"
                      _hover={{ borderColor: "border.emphasized" }}
                      _focus={{
                        borderColor: "colorPalette.500",
                        boxShadow: "0 0 0 1px var(--chakra-colors-colorPalette-500)"
                      }}
                      transition="all 0.2s"
                    />
                    <Combobox.Trigger
                      position="absolute"
                      right="0.5rem"
                      top="50%"
                      transform="translateY(-50%)"
                      color="fg.muted"
                    >
                      <FaChevronDown size={10} />
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

          <HStack
            gap={2}
            align="center"
            px={3}
            height="40px"
            borderRadius="md"
            bg="bg"
            borderWidth="1px"
            borderColor="border"
          >
            <Text fontSize="sm" fontWeight="medium" color="fg.muted">
              Sort by:
            </Text>
            <Button
              size="sm"
              variant={sortBy === 'name' ? 'solid' : 'ghost'}
              onClick={() => handleSortToggle('name')}
              bg={sortBy === 'name' ? "colorPalette.100" : 'transparent'}
              color={sortBy === 'name' ? "colorPalette.700" : "fg"}
              _hover={{
                bg: sortBy === 'name' ? "colorPalette.200" : "bg.muted",
                transform: "translateY(-1px)"
              }}
              _active={{ transform: "translateY(0)" }}
              borderRadius="md"
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
              bg={sortBy === 'updated_at' ? "colorPalette.100" : 'transparent'}
              color={sortBy === 'updated_at' ? "colorPalette.700" : "fg"}
              _hover={{
                bg: sortBy === 'updated_at' ? "colorPalette.200" : "bg.muted",
                transform: "translateY(-1px)"
              }}
              _active={{ transform: "translateY(0)" }}
              borderRadius="md"
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

        <HStack justify="space-between" pt={2} borderTopWidth="1px" borderColor="border">
          <Text fontSize="sm" fontWeight="medium" color="fg.muted">
            {totalPrompts} prompt{totalPrompts !== 1 ? 's' : ''} found
          </Text>
          {repoFilter && (
            <HStack gap={2}>
              <Text fontSize="sm" color="fg.muted">Filtered by:</Text>
              <Text
                fontSize="sm"
                fontWeight="semibold"
                px={2}
                py={1}
                borderRadius="md"
                bg="colorPalette.100"
                color="colorPalette.700"
              >
                {repoFilter}
              </Text>
            </HStack>
          )}
        </HStack>
      </VStack>
    </Box>
  );
}