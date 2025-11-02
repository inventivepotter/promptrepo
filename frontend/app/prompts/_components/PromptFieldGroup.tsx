'use client';

import {
  VStack,
  Input,
  Textarea,
  Field,
  Card,
  HStack,
  Badge,
  Fieldset,
  Stack,
  IconButton,
  Button,
  Collapsible,
  Text,
} from '@chakra-ui/react';
import { useState } from 'react';
import { FaTimes } from 'react-icons/fa';
import { LuChevronDown, LuChevronUp } from 'react-icons/lu';
import { useCurrentPrompt, usePromptActions } from '@/stores/promptStore/hooks';
import { FaGitAlt, FaFolder } from 'react-icons/fa';

interface PromptFieldGroupProps {
  repoName: string;
  filePath: string;
}

export function PromptFieldGroup({ repoName, filePath }: PromptFieldGroupProps) {
  const currentPrompt = useCurrentPrompt();
  const { setCurrentPrompt } = usePromptActions();
  const [tagInput, setTagInput] = useState('');
  const [showPromptDetails, setShowPromptDetails] = useState(true);

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
    <Card.Root position="relative">
      {/* Badges positioned on the border */}
      <HStack
        position="absolute"
        top="-12px"
        right="16px"
        gap={2}
        fontSize="xs"
        zIndex={1}
      >
        <Badge variant="subtle" colorPalette="green" display="flex" alignItems="center" gap={1}>
          <FaGitAlt />
          {repoName}
        </Badge>
        <Badge variant="subtle" colorPalette="gray" opacity={0.8} display="flex" alignItems="center" gap={1}>
          <FaFolder />
          {filePath}
        </Badge>
      </HStack>

      <Card.Body pt={6}>
        <Fieldset.Root>
          <HStack justify="space-between" align="center">
            <Stack flex={1}>
              <Fieldset.Legend>Prompt Details</Fieldset.Legend>
              <Fieldset.HelperText color="text.tertiary">Configure the basic prompt information and content</Fieldset.HelperText>
            </Stack>
            <Button
              variant="ghost"
              _hover={{ bg: "bg.subtle" }}
              size="sm"
              onClick={() => setShowPromptDetails(!showPromptDetails)}
              aria-label={showPromptDetails ? "Collapse prompt details" : "Expand prompt details"}
            >
              <HStack gap={1}>
                <Text fontSize="xs" fontWeight="medium">
                  {showPromptDetails ? "Hide" : "Show"}
                </Text>
                {showPromptDetails ? <LuChevronUp /> : <LuChevronDown />}
              </HStack>
            </Button>
          </HStack>

          <Fieldset.Content>
            <Collapsible.Root open={showPromptDetails}>
              <Collapsible.Content>
                <VStack gap={4} align="stretch" mt={3}>
          {/* Name - Primary Field */}
          <Field.Root required>
            <Field.Label fontSize="xs" fontWeight="medium">Name <Field.RequiredIndicator /></Field.Label>
            <Input
              value={prompt?.name || ''}
              onChange={(e) => updateField('name', e.target.value)}
              placeholder="Enter prompt name"
              size="md"
            />
          </Field.Root>

          {/* Prompt Content - Main Focus */}
          <Field.Root required>
            <Field.Label fontSize="xs" fontWeight="medium">Prompt <Field.RequiredIndicator /></Field.Label>
            <Textarea
              value={prompt?.prompt || ''}
              onChange={(e) => updateField('prompt', e.target.value)}
              placeholder="Enter the main prompt content..."
              rows={12}
              minH="350px"
              lineHeight="1.7"
              resize="vertical"
            />
          </Field.Root>

          {/* Description - Secondary Field */}
          <Field.Root>
            <Field.Label fontSize="xs" fontWeight="medium">Description <Field.RequiredIndicator opacity={0.4}>(optional)</Field.RequiredIndicator></Field.Label>
            <Textarea
              value={prompt?.description || ''}
              onChange={(e) => updateField('description', e.target.value)}
              placeholder="Brief description of what this prompt does"
              rows={2}
              resize="vertical"
            />
          </Field.Root>

          {/* Tags - Optional Field */}
          <Field.Root>
            <Field.Label fontSize="xs" fontWeight="medium">Tags <Field.RequiredIndicator opacity={0.4}>(optional)</Field.RequiredIndicator></Field.Label>
            <Input
              value={tagInput}
              onChange={(e) => setTagInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && tagInput.trim()) {
                  e.preventDefault();
                  const currentTags = Array.isArray(prompt?.tags) ? prompt.tags : [];
                  if (!currentTags.includes(tagInput.trim())) {
                    updateField('tags', [...currentTags, tagInput.trim()]);
                  }
                  setTagInput('');
                }
              }}
              placeholder="Type and press Enter"
              size="md"
            />
            {Array.isArray(prompt?.tags) && prompt.tags.length > 0 && (
              <HStack gap={1} flexWrap="wrap" mt={2}>
                {prompt.tags.map((tag, index) => (
                  <Badge
                    key={index}
                    variant="subtle"
                    colorPalette="purple"
                    display="flex"
                    alignItems="center"
                    gap={1}
                    pr={1}
                  >
                    {tag}
                    <IconButton
                      aria-label={`Remove ${tag}`}
                      size="2xs"
                      variant="ghost"
                      colorPalette="purple"
                      onClick={() => {
                        const newTags = (prompt?.tags || []).filter((_, i) => i !== index);
                        updateField('tags', newTags);
                      }}
                    >
                      <FaTimes />
                    </IconButton>
                  </Badge>
                ))}
              </HStack>
            )}
          </Field.Root>
                </VStack>
              </Collapsible.Content>
            </Collapsible.Root>
          </Fieldset.Content>
        </Fieldset.Root>
      </Card.Body>
    </Card.Root>
  );
}