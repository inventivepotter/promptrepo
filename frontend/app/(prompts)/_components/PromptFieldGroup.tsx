'use client';

import React from 'react';
import {
  Box,
  VStack,
  Input,
  Textarea,
  Combobox,
  createListCollection,
  Field,
} from '@chakra-ui/react';
import { FaChevronDown } from 'react-icons/fa';
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

  // Check if current repo exists and matches one of the available repos
  const isRepoDisabled = Boolean(formData.repo?.id && configuredRepos.some(repo => repo.id === formData.repo?.id));

  // Filter repositories based on search value
  const filteredRepos = configuredRepos.filter(repo =>
    repo.name.toLowerCase().includes(repoSearchValue.toLowerCase()) ||
    repo.id.toString().toLowerCase().includes(repoSearchValue.toLowerCase())
  );

  return (
    <Box as="form">
      <VStack gap={6} align="stretch">
        {/* Repository Field */}
        <Field.Root
          required
          invalid={showRepoError && !formData.repo}
        >
          <Field.Label>Repository</Field.Label>
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
          {showRepoError && !formData.repo && (
            <Field.ErrorText>Please select a repository before editing other fields</Field.ErrorText>
          )}
        </Field.Root>

        {/* Name Field */}
        <Field.Root
          required
          disabled={!formData.repo}
        >
          <Field.Label>Name</Field.Label>
          <Input
            value={formData.name || ''}
            onChange={(e) => updateField('name', e.target.value)}
            placeholder="Enter prompt name"
            disabled={!formData.repo}
          />
        </Field.Root>

        {/* Description Field */}
        <Field.Root disabled={!formData.repo}>
          <Field.Label>Description</Field.Label>
          <Textarea
            value={formData.description || ''}
            onChange={(e) => updateField('description', e.target.value)}
            placeholder="Enter prompt description (optional)"
            rows={2}
            resize="vertical"
            disabled={!formData.repo}
          />
        </Field.Root>

        {/* File Path Field */}
        <Field.Root
          required
          disabled={!formData.repo}
        >
          <Field.Label>File Path</Field.Label>
          <Input
            value={formData.file_path || ''}
            onChange={(e) => updateField('file_path', e.target.value)}
            placeholder="e.g., prompts/my-prompt.yaml"
            disabled={!formData.repo}
          />
        </Field.Root>

        {/* Category Field */}
        <Field.Root disabled={!formData.repo}>
          <Field.Label>Category</Field.Label>
          <Input
            value={formData.category || ''}
            onChange={(e) => updateField('category', e.target.value)}
            placeholder="Enter category (optional)"
            disabled={!formData.repo}
          />
        </Field.Root>

        {/* Tags Field */}
        <Field.Root disabled={!formData.repo}>
          <Field.Label>Tags</Field.Label>
          <Input
            value={Array.isArray(formData.tags) ? formData.tags.join(', ') : ''}
            onChange={(e) => {
              const tagsArray = e.target.value.split(',').map(tag => tag.trim()).filter(tag => tag);
              updateField('tags' as keyof Prompt, tagsArray as unknown as string);
            }}
            placeholder="e.g., coding, debugging, refactoring"
            disabled={!formData.repo}
          />
        </Field.Root>

        {/* System Prompt Field */}
        <Field.Root disabled={!formData.repo}>
          <Field.Label>System Prompt</Field.Label>
          <Textarea
            value={formData.system_prompt || ''}
            onChange={(e) => updateField('system_prompt', e.target.value)}
            placeholder="Enter system prompt (optional)..."
            rows={8}
            minH="200px"
            lineHeight="1.6"
            resize="vertical"
            disabled={!formData.repo}
          />
        </Field.Root>

        {/* User Prompt Field */}
        <Field.Root disabled={!formData.repo}>
          <Field.Label>User Prompt</Field.Label>
          <Textarea
            value={formData.user_prompt || ''}
            onChange={(e) => updateField('user_prompt', e.target.value)}
            placeholder="Enter user prompt (optional)..."
            rows={8}
            minH="200px"
            lineHeight="1.6"
            resize="vertical"
            disabled={!formData.repo}
          />
        </Field.Root>

        {/* Content Field */}
        <Field.Root disabled={!formData.repo}>
          <Field.Label>Full Content (Combined)</Field.Label>
          <Textarea
            value={formData.content || ''}
            onChange={(e) => updateField('content', e.target.value)}
            placeholder="Full prompt content..."
            rows={15}
            minH="400px"
            lineHeight="1.6"
            resize="vertical"
            disabled={!formData.repo}
          />
        </Field.Root>
      </VStack>
    </Box>
  );
}