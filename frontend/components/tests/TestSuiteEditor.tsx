'use client';

import React, { useState } from 'react';
import {
  Card,
  VStack,
  HStack,
  Text,
  Input,
  Textarea,
  Field,
  Collapsible,
  Button,
  Fieldset,
  Stack,
} from '@chakra-ui/react';
import { LuChevronDown, LuChevronUp } from 'react-icons/lu';
import type { TestSuiteDefinition, MetricConfig } from '@/types/test';
import { MetricSelector } from './MetricSelector';

export interface TestSuiteEditorProps {
  suite: TestSuiteDefinition;
  onChange: (suite: TestSuiteDefinition) => void;
}

export function TestSuiteEditor({ suite, onChange }: TestSuiteEditorProps) {
  const [isOpen, setIsOpen] = useState(true);
  const [showMetrics, setShowMetrics] = useState(true);
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


  const handleMetricsChange = (metrics: MetricConfig[]) => {
    onChange({
      ...suite,
      metrics,
      updated_at: new Date().toISOString(),
    });
  };

  return (
    <VStack gap={6} align="stretch">
      {/* Test Suite Information Section */}
      <Card.Root>
        <Card.Body>
          <Fieldset.Root>
            <HStack justify="space-between" align="center">
              <Stack flex={1}>
                <Fieldset.Legend>Test Suite Information</Fieldset.Legend>
                <Fieldset.HelperText color="text.tertiary">
                  Configure the basic information and metadata for this test suite
                </Fieldset.HelperText>
              </Stack>
              <Button
                variant="ghost"
                _hover={{ bg: "bg.subtle" }}
                size="sm"
                onClick={() => setIsOpen(!isOpen)}
                aria-label={isOpen ? "Collapse test suite information" : "Expand test suite information"}
              >
                <HStack gap={1}>
                  <Text fontSize="xs" fontWeight="medium">
                    {isOpen ? "Hide" : "Show"}
                  </Text>
                  {isOpen ? <LuChevronUp /> : <LuChevronDown />}
                </HStack>
              </Button>
            </HStack>

            <Fieldset.Content>
              <Collapsible.Root open={isOpen}>
                <Collapsible.Content>
                  <VStack gap={4} align="stretch" mt={3}>
                    <Field.Root required>
                      <Field.Label fontSize="xs" fontWeight="medium">
                        Suite Name <Field.RequiredIndicator />
                      </Field.Label>
                      <Input
                        value={suite.name}
                        onChange={handleNameChange}
                        placeholder="Enter test suite name"
                        size="md"
                      />
                    </Field.Root>

                    <Field.Root>
                      <Field.Label fontSize="xs" fontWeight="medium">
                        Description <Field.RequiredIndicator opacity={0.4}>(optional)</Field.RequiredIndicator>
                      </Field.Label>
                      <Textarea
                        value={suite.description || ''}
                        onChange={handleDescriptionChange}
                        placeholder="Describe the purpose of this test suite"
                        rows={2}
                        resize="vertical"
                      />
                    </Field.Root>
                  </VStack>
                </Collapsible.Content>
              </Collapsible.Root>
            </Fieldset.Content>
          </Fieldset.Root>
        </Card.Body>
      </Card.Root>

      {/* Evaluation Metrics Section */}
      <Card.Root>
        <Card.Body>
          <Fieldset.Root>
            <HStack justify="space-between" align="center">
              <Stack flex={1}>
                <Fieldset.Legend>Evaluation Metrics</Fieldset.Legend>
                <Fieldset.HelperText color="text.tertiary">
                  Choose how to measure test passed/failed
                </Fieldset.HelperText>
              </Stack>
              <Button
                variant="ghost"
                _hover={{ bg: "bg.subtle" }}
                size="sm"
                onClick={() => setShowMetrics(!showMetrics)}
                aria-label={showMetrics ? "Collapse evaluation metrics" : "Expand evaluation metrics"}
              >
                <HStack gap={1}>
                  <Text fontSize="xs" fontWeight="medium">
                    {showMetrics ? "Hide" : "Show"}
                  </Text>
                  {showMetrics ? <LuChevronUp /> : <LuChevronDown />}
                </HStack>
              </Button>
            </HStack>

            <Fieldset.Content>
              <Collapsible.Root open={showMetrics}>
                <Collapsible.Content>
                  <MetricSelector
                    metrics={suite.metrics || []}
                    onChange={handleMetricsChange}
                  />
                </Collapsible.Content>
              </Collapsible.Root>
            </Fieldset.Content>
          </Fieldset.Root>
        </Card.Body>
      </Card.Root>
    </VStack>
  );
}