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
import { SelectedRepo } from './Repos';
import { Prompt } from '../_state/promptState';

interface PromptFieldGroupProps {
  formData: Partial<Prompt>;
  selectedRepos: Array<SelectedRepo>;
  showRepoError: boolean;
  updateField: (field: keyof Prompt, value: string | number | boolean) => void;
  updateRepoField: (repo: SelectedRepo | undefined) => void;
}

export function PromptFieldGroup({
  formData,
  selectedRepos,
  showRepoError,
  updateField,
  updateRepoField
}: PromptFieldGroupProps) {
  const mutedTextColor = useColorModeValue('gray.600', 'gray.400');

  return (
    <Box>
      <Text fontSize="lg" fontWeight="semibold" mb={4}>
        Basic Information
      </Text>
      <VStack gap={4} align="stretch">
        <Box>
          <Text mb={2} fontWeight="semibold" color={!formData.repo ? "red.500" : undefined}>
            Repository *
          </Text>
          {showRepoError && !formData.repo && (
            <Text fontSize="sm" color="red.500" mb={2}>
              Please select a repository before editing other fields
            </Text>
          )}
        </Box>

        <Combobox.Root
          collection={createListCollection({
            items: selectedRepos.map(repo => ({
              label: `${repo.name} (${repo.branch})`,
              value: repo.id.toString()
            }))
          })}
          value={formData.repo?.id ? [formData.repo.id.toString()] : []}
          onValueChange={(e) => {
            const id = parseInt(e.value[0] || '0');
            const selectedRepo = selectedRepos.find(r => r.id === id);
            if (selectedRepo) {
              updateRepoField({
                id: selectedRepo.id,
                branch: selectedRepo.branch,
                name: selectedRepo.name
              });
            } else {
              updateRepoField(undefined);
            }
          }}
          openOnClick
        >
          <Combobox.Control position="relative">
            <Combobox.Input
              placeholder={selectedRepos.length > 0 ? "Select repository" : "No repositories configured"}
              paddingRight="2rem"
            />
            <Combobox.Trigger position="absolute" right="0.5rem" top="50%" transform="translateY(-50%)">
              <FaChevronDown size={16} />
            </Combobox.Trigger>
          </Combobox.Control>
          <Combobox.Positioner>
            <Combobox.Content>
              {selectedRepos.map(repo => (
                <Combobox.Item key={repo.id} item={repo.id.toString()}>
                  <Combobox.ItemText>{repo.name} ({repo.branch})</Combobox.ItemText>
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