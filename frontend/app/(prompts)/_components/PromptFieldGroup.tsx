'use client';

import React from 'react';
import {
  Box,
  VStack,
  Text,
  Input,
  Textarea,
  Combobox,
  createListCollection,
} from '@chakra-ui/react';
import { FaChevronDown } from 'react-icons/fa';
import { useColorModeValue } from '@/components/ui/color-mode';
import { Repo } from '@/types/Repo';
import { Prompt } from '@/types/Prompt';

interface PromptFieldGroupProps {
  formData: Partial<Prompt>;
  configuredRepos: Array<Repo>;
  showRepoError: boolean;
  updateField: (field: keyof Prompt, value: string | number | boolean) => void;
  updateRepoField: (repo: Repo | undefined) => void;
}

export function PromptFieldGroup({
  formData,
  configuredRepos,
  showRepoError,
  updateField,
  updateRepoField
}: PromptFieldGroupProps) {
  const mutedTextColor = useColorModeValue('gray.600', 'gray.400');

  // Check if current repo exists and matches one of the available repos
  const isRepoDisabled = Boolean(formData.repo?.id && configuredRepos.some(repo => repo.id === formData.repo?.id));

  return (
    <Box>
      <Text fontSize="lg" fontWeight="semibold" mb={4}>
        Basic Information
      </Text>
      <VStack gap={4} align="stretch">
        <Box>
          <Text mb={2} fontWeight="semibold" color={!isRepoDisabled ? "red.500" : undefined} opacity={0.7}>
            Repository
          </Text>
          {showRepoError && !formData.repo && (
            <Text fontSize="sm" color="red.500" mb={2}>
              Please select a repository before editing other fields
            </Text>
          )}
        </Box>

        <Combobox.Root
          collection={createListCollection({
            items: configuredRepos.map(repo => ({
              label: repo.name,
              value: repo.id
            }))
          })}
          value={formData.repo?.id ? [formData.repo.id] : []}
          onValueChange={(e) => {
            const id = e.value[0] || '0';
            const selectedRepo = configuredRepos.find(r => r.id === id);
            if (selectedRepo) {
              updateRepoField({
                id: selectedRepo.id,
                base_branch: selectedRepo.base_branch,
                name: selectedRepo.name
              });
            } else {
              updateRepoField(undefined);
            }
          }}
          openOnClick
          disabled={isRepoDisabled}
        >
          <Combobox.Control position="relative">
            <Combobox.Input
              placeholder={configuredRepos.length > 0 ? "Select repository" : "No repositories configured"}
              paddingRight="2rem"
            />
            <Combobox.Trigger position="absolute" right="0.5rem" top="50%" transform="translateY(-50%)">
              <FaChevronDown size={16} />
            </Combobox.Trigger>
          </Combobox.Control>
          <Combobox.Positioner>
            <Combobox.Content>
              {configuredRepos.map(repo => (
                <Combobox.Item key={repo.id} item={repo.id.toString()}>
                  <Combobox.ItemText>{repo.name}</Combobox.ItemText>
                  <Combobox.ItemIndicator />
                </Combobox.Item>
              ))}
            </Combobox.Content>
          </Combobox.Positioner>
        </Combobox.Root>

        <Box opacity={!formData.repo ? 0.5 : 1}>
          <Text mb={2} fontWeight={formData.repo ? "medium" : "normal"} color={!formData.repo ? "gray.400" : undefined}>Name</Text>
          <Input
            value={formData.name || ''}
            onChange={(e) => updateField('name', e.target.value)}
            placeholder="Enter prompt name"
          />
        </Box>

        <Box opacity={!formData.repo ? 0.5 : 1}>
          <Text mb={2} fontWeight={formData.repo ? "medium" : "normal"} color={!formData.repo ? "gray.400" : undefined} fontSize="lg">Prompt Template</Text>
          <Text mb={3} fontSize="sm" color={mutedTextColor}>
            This is the core of your prompt. Write your instructions, context, and any variables here.
          </Text>
          <Textarea
            value={formData.prompt || ''}
            onChange={(e) => updateField('prompt', e.target.value)}
            placeholder="Enter your prompt template here..."
            rows={15}
            minH="400px"
            lineHeight="1.6"
            resize="vertical"
          />
        </Box>
      </VStack>
    </Box>
  );
}