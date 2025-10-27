'use client';

import React from 'react';
import {
  Card,
  VStack,
  HStack,
  Text,
  Input,
  Textarea,
  Heading,
  Field,
} from '@chakra-ui/react';
import type { TestSuiteDefinition } from '@/types/test';

export interface TestSuiteEditorProps {
  suite: TestSuiteDefinition;
  onChange: (suite: TestSuiteDefinition) => void;
}

export function TestSuiteEditor({ suite, onChange }: TestSuiteEditorProps) {
  const handleNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange({
      ...suite,
      name: e.target.value,
      updated_at: new Date().toISOString(),
    });
  };

  const handleDescriptionChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    onChange({
      ...suite,
      description: e.target.value,
      updated_at: new Date().toISOString(),
    });
  };

  const handleTagsChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const tags = e.target.value.split(',').map(tag => tag.trim()).filter(Boolean);
    onChange({
      ...suite,
      tags,
      updated_at: new Date().toISOString(),
    });
  };

  return (
    <Card.Root>
      <Card.Header>
        <Heading size="md">Test Suite Information</Heading>
      </Card.Header>
      <Card.Body>
        <VStack gap={4} align="stretch">
          <Field.Root required>
            <Field.Label>Suite Name <Field.RequiredIndicator /></Field.Label>
            <Input
              value={suite.name}
              onChange={handleNameChange}
              placeholder="Enter test suite name"
            />
          </Field.Root>

          <Field.Root>
            <Field.Label>Description</Field.Label>
            <Textarea
              value={suite.description || ''}
              onChange={handleDescriptionChange}
              placeholder="Describe the purpose of this test suite"
              rows={3}
            />
          </Field.Root>

          <Field.Root>
            <Field.Label>Tags</Field.Label>
            <Input
              value={suite.tags.join(', ')}
              onChange={handleTagsChange}
              placeholder="e.g., production, critical, regression"
            />
            <Field.HelperText>Comma-separated tags for organization</Field.HelperText>
          </Field.Root>

          <HStack justify="space-between" pt={2} borderTopWidth="1px">
            <VStack align="start" gap={0}>
              <Text fontSize="xs" color="fg.subtle">Created</Text>
              <Text fontSize="sm">{new Date(suite.created_at).toLocaleString()}</Text>
            </VStack>
            <VStack align="end" gap={0}>
              <Text fontSize="xs" color="fg.subtle">Last Updated</Text>
              <Text fontSize="sm">{new Date(suite.updated_at).toLocaleString()}</Text>
            </VStack>
          </HStack>
        </VStack>
      </Card.Body>
    </Card.Root>
  );
}