'use client';

import { useState } from 'react';
import {
  Box,
  VStack,
  Input,
  Textarea,
  Combobox,
  createListCollection,
  Field,
  Switch,
} from '@chakra-ui/react';
import { FaChevronDown } from 'react-icons/fa';
import { useCurrentPrompt, usePromptActions, useModelOptions } from '@/stores/promptStore/hooks';

export function PromptFieldGroup() {
  const currentPrompt = useCurrentPrompt();
  const { setCurrentPrompt } = usePromptActions();
  const modelOptions = useModelOptions();
  const [modelSearchValue, setModelSearchValue] = useState('');

  if (!currentPrompt) {
    return <Box>No prompt selected</Box>;
  }

  const updateField = (field: string, value: string | number | boolean | string[] | null | Record<string, unknown>) => {
    if (!currentPrompt) return;
    
    setCurrentPrompt({
      ...currentPrompt,
      prompt: {
        ...currentPrompt.prompt,
        [field]: value,
      },
    });
  };

  const filteredModels = modelOptions.filter(opt =>
    opt.label.toLowerCase().includes(modelSearchValue.toLowerCase())
  );

  const { prompt } = currentPrompt;
  const currentModelValue = prompt?.provider && prompt?.model
    ? `${prompt.provider}:${prompt.model}`
    : '';

  return (
    <Box as="form">
      <VStack gap={6} align="stretch">
        {/* Repository (read-only) */}
        <Field.Root>
          <Field.Label>Repository</Field.Label>
          <Input value={currentPrompt.repo_name} disabled />
        </Field.Root>

        {/* File Path (read-only) */}
        <Field.Root>
          <Field.Label>File Path</Field.Label>
          <Input value={currentPrompt.file_path} disabled />
        </Field.Root>

        {/* Name */}
        <Field.Root required>
          <Field.Label>Name</Field.Label>
          <Input
            value={prompt?.name || ''}
            onChange={(e) => updateField('name', e.target.value)}
            placeholder="Enter prompt name"
          />
        </Field.Root>

        {/* Description */}
        <Field.Root>
          <Field.Label>Description</Field.Label>
          <Textarea
            value={prompt?.description || ''}
            onChange={(e) => updateField('description', e.target.value)}
            placeholder="Enter prompt description (optional)"
            rows={2}
            resize="vertical"
          />
        </Field.Root>

        {/* Category */}
        <Field.Root>
          <Field.Label>Category</Field.Label>
          <Input
            value={prompt?.category || ''}
            onChange={(e) => updateField('category', e.target.value)}
            placeholder="Enter category (optional)"
          />
        </Field.Root>

        {/* Prompt Content */}
        <Field.Root required>
          <Field.Label>Prompt</Field.Label>
          <Textarea
            value={prompt?.prompt || ''}
            onChange={(e) => updateField('prompt', e.target.value)}
            placeholder="Enter the main prompt content..."
            rows={10}
            minH="300px"
            lineHeight="1.6"
            resize="vertical"
          />
        </Field.Root>

        {/* Tags */}
        <Field.Root>
          <Field.Label>Tags</Field.Label>
          <Input
            value={Array.isArray(prompt?.tags) ? prompt.tags.join(', ') : ''}
            onChange={(e) => {
              const tagsArray = e.target.value.split(',').map(tag => tag.trim()).filter(tag => tag);
              updateField('tags', tagsArray);
            }}
            placeholder="e.g., coding, debugging, refactoring"
          />
        </Field.Root>

      </VStack>
    </Box>
  );
}