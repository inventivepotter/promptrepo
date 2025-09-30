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
  const [repoSearchValue, setRepoSearchValue] = React.useState('');
  const mutedTextColor = useColorModeValue('gray.600', 'gray.400');

  // Check if current repo exists and matches one of the available repos
  const isRepoDisabled = Boolean(formData.repo?.id && configuredRepos.some(repo => repo.id === formData.repo?.id));

  // Filter repositories based on search value
  const filteredRepos = configuredRepos.filter(repo =>
    repo.name.toLowerCase().includes(repoSearchValue.toLowerCase()) ||
    repo.id.toString().toLowerCase().includes(repoSearchValue.toLowerCase())
  );

  return (
    <Box>
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
          <Combobox.Root
          collection={createListCollection({
            items: filteredRepos.map(repo => ({
              label: repo.name,
              value: repo.id
            }))
          })}
          value={formData.repo?.id ? [formData.repo.id] : []}
          onValueChange={(e) => {
            const id = e.value[0] || '0';
            const selectedRepo = configuredRepos.find(r => r.id === id);
            if (selectedRepo) {
              updateRepoField(selectedRepo);
            } else {
              updateRepoField(undefined);
            }
          }}
          inputValue={repoSearchValue}
          onInputValueChange={(e) => setRepoSearchValue(e.inputValue)}
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
              {filteredRepos.map(repo => (
                <Combobox.Item key={repo.id} item={repo.id.toString()}>
                  <Combobox.ItemText>{repo.name}</Combobox.ItemText>
                  <Combobox.ItemIndicator />
                </Combobox.Item>
              ))}
            </Combobox.Content>
          </Combobox.Positioner>
          </Combobox.Root>
        </Box>

        <Box opacity={!formData.repo ? 0.5 : 1}>
          <Text mb={2} fontWeight={formData.repo ? "medium" : "normal"} color={!formData.repo ? "gray.400" : undefined}>Name</Text>
          <Input
            value={formData.name || ''}
            onChange={(e) => updateField('name', e.target.value)}
            placeholder="Enter prompt name"
          />
        </Box>

        <Box opacity={!formData.repo ? 0.5 : 1}>
          <Text mb={2} fontWeight={formData.repo ? "medium" : "normal"} color={!formData.repo ? "gray.400" : undefined}>Description</Text>
          <Textarea
            value={formData.description || ''}
            onChange={(e) => updateField('description', e.target.value)}
            placeholder="Enter prompt description (optional)"
            rows={2}
            resize="vertical"
          />
        </Box>

        <Box opacity={!formData.repo ? 0.5 : 1}>
          <Text mb={2} fontWeight={formData.repo ? "medium" : "normal"} color={!formData.repo ? "gray.400" : undefined}>Category</Text>
          <Input
            value={formData.category || ''}
            onChange={(e) => updateField('category', e.target.value)}
            placeholder="Enter category (optional)"
          />
        </Box>

        <Box opacity={!formData.repo ? 0.5 : 1}>
          <Text mb={2} fontWeight={formData.repo ? "medium" : "normal"} color={!formData.repo ? "gray.400" : undefined}>Tags</Text>
          <Text mb={2} fontSize="sm" color={mutedTextColor}>
            Enter tags separated by commas
          </Text>
          <Input
            value={Array.isArray(formData.tags) ? formData.tags.join(', ') : ''}
            onChange={(e) => {
              const tagsArray = e.target.value.split(',').map(tag => tag.trim()).filter(tag => tag);
              updateField('tags' as keyof Prompt, tagsArray as unknown as string);
            }}
            placeholder="e.g., coding, debugging, refactoring"
          />
        </Box>

        <Box opacity={!formData.repo ? 0.5 : 1}>
          <Text mb={2} fontWeight={formData.repo ? "medium" : "normal"} color={!formData.repo ? "gray.400" : undefined} fontSize="lg">System Prompt</Text>
          <Text mb={3} fontSize="sm" color={mutedTextColor}>
            The system prompt sets the behavior and context for the AI assistant.
          </Text>
          <Textarea
            value={formData.system_prompt || ''}
            onChange={(e) => updateField('system_prompt', e.target.value)}
            placeholder="Enter system prompt (optional)..."
            rows={8}
            minH="200px"
            lineHeight="1.6"
            resize="vertical"
          />
        </Box>

        <Box opacity={!formData.repo ? 0.5 : 1}>
          <Text mb={2} fontWeight={formData.repo ? "medium" : "normal"} color={!formData.repo ? "gray.400" : undefined} fontSize="lg">User Prompt</Text>
          <Text mb={3} fontSize="sm" color={mutedTextColor}>
            The user prompt is the main instruction or query to the AI.
          </Text>
          <Textarea
            value={formData.user_prompt || ''}
            onChange={(e) => updateField('user_prompt', e.target.value)}
            placeholder="Enter user prompt (optional)..."
            rows={8}
            minH="200px"
            lineHeight="1.6"
            resize="vertical"
          />
        </Box>

        <Box opacity={!formData.repo ? 0.5 : 1}>
          <Text mb={2} fontWeight={formData.repo ? "medium" : "normal"} color={!formData.repo ? "gray.400" : undefined} fontSize="lg">Full Content (Combined)</Text>
          <Text mb={3} fontSize="sm" color={mutedTextColor}>
            This is the complete prompt content that will be stored. Edit system and user prompts above, or edit this directly.
          </Text>
          <Textarea
            value={formData.content || ''}
            onChange={(e) => updateField('content', e.target.value)}
            placeholder="Full prompt content..."
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