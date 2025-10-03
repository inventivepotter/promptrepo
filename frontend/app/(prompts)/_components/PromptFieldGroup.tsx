'use client';

import {
  VStack,
  Input,
  Textarea,
  Field,
  Fieldset,
  Stack,
  Card,
} from '@chakra-ui/react';
import { useCurrentPrompt, usePromptActions } from '@/stores/promptStore/hooks';

export function PromptFieldGroup() {
  const currentPrompt = useCurrentPrompt();
  const { setCurrentPrompt } = usePromptActions();

  if (!currentPrompt) {
    return null;
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

  const { prompt } = currentPrompt;

  return (
    <VStack gap={6} align="stretch">
      {/* Repository & Path Group */}
      <Card.Root>
        <Card.Body>
          <Fieldset.Root size="lg">
            <Stack>
              <Fieldset.Legend>Repository Information</Fieldset.Legend>
              <Fieldset.HelperText>
                Source repository and file location
              </Fieldset.HelperText>
            </Stack>

            <Fieldset.Content>
              <Field.Root>
                <Field.Label>Repository</Field.Label>
                <Input value={currentPrompt.repo_name} disabled />
              </Field.Root>

              <Field.Root>
                <Field.Label>File Path</Field.Label>
                <Input value={currentPrompt.file_path} disabled />
              </Field.Root>
            </Fieldset.Content>
          </Fieldset.Root>
        </Card.Body>
      </Card.Root>

      {/* Prompt Details Group */}
      <Card.Root>
        <Card.Body>
          <Fieldset.Root size="lg">
            <Stack>
              <Fieldset.Legend>Prompt Details</Fieldset.Legend>
              <Fieldset.HelperText>
                Configure the basic prompt information
              </Fieldset.HelperText>
            </Stack>

            <Fieldset.Content>
          <Field.Root required>
            <Field.Label>Name</Field.Label>
            <Input
              value={prompt?.name || ''}
              onChange={(e) => updateField('name', e.target.value)}
              placeholder="Enter prompt name"
            />
          </Field.Root>

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

          <Field.Root>
            <Field.Label>Category</Field.Label>
            <Input
              value={prompt?.category || ''}
              onChange={(e) => updateField('category', e.target.value)}
              placeholder="Enter category (optional)"
            />
          </Field.Root>

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
            </Fieldset.Content>
          </Fieldset.Root>
        </Card.Body>
      </Card.Root>
    </VStack>
  );
}