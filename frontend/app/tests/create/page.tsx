'use client';

import React, { useEffect, useState, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import {
  Box,
  Container,
  VStack,
  HStack,
  Text,
  Button,
  Card,
  Field,
  Input,
  Textarea,
  ScrollArea,
  Heading,
} from '@chakra-ui/react';
import { LuArrowLeft, LuSave } from 'react-icons/lu';
import { useTestStore } from '@/stores/testStore/testStore';
import { useSelectedRepository } from '@/stores/repositoryFilterStore';
import { TemplateVariableEditor } from '@/components/tests/TemplateVariableEditor';
import { MetricSelector } from '@/components/tests/MetricSelector';
import { PromptSelector } from '@/components/tests/PromptSelector';
import { LoadingOverlay } from '@/components/LoadingOverlay';
import type { UnitTestDefinition, MetricConfig } from '@/types/test';
import type { components } from '@/types/generated/api';
import { TemplateUtils } from '@/services/prompts';

type PromptMeta = components['schemas']['PromptMeta'];

function TestCreatePageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const selectedRepository = useSelectedRepository();
  const repoName = searchParams.get('repo_name') || selectedRepository;

  const [testName, setTestName] = useState('');
  const [description, setDescription] = useState('');
  const [testSuiteName, setTestSuiteName] = useState('');
  const [promptReference, setPromptReference] = useState('');
  const [userMessage, setUserMessage] = useState('');
  const [templateVariables, setTemplateVariables] = useState<Record<string, unknown>>({});
  const [expectedOutput, setExpectedOutput] = useState('');
  const [metrics, setMetrics] = useState<MetricConfig[]>([]);

  const testSuites = useTestStore((state) => state.testSuites);
  const fetchTestSuites = useTestStore((state) => state.fetchTestSuites);
  const fetchTestSuite = useTestStore((state) => state.fetchTestSuite);
  const saveTestSuite = useTestStore((state) => state.saveTestSuite);
  const currentSuite = useTestStore((state) => state.currentSuite);
  const isLoading = useTestStore((state) => state.isLoading);

  // Fetch test suites on mount
  useEffect(() => {
    if (repoName) {
      fetchTestSuites(repoName);
    }
  }, [repoName, fetchTestSuites]);

  // Fetch suite when selected
  useEffect(() => {
    if (repoName && testSuiteName) {
      fetchTestSuite(repoName, testSuiteName);
    }
  }, [repoName, testSuiteName, fetchTestSuite]);

  const handlePromptSelection = (promptPath: string, promptMeta?: PromptMeta) => {
    setPromptReference(promptPath);
    
    if (promptMeta?.prompt?.prompt) {
      const variables = TemplateUtils.extractVariables(promptMeta.prompt.prompt)
        .filter(v => v !== 'user_message');
      
      const newVariables: Record<string, unknown> = {};
      variables.forEach(varName => {
        newVariables[varName] = templateVariables[varName] ?? '';
      });
      
      setTemplateVariables(newVariables);
    }
  };

  const handleSave = async () => {
    if (!repoName || !testSuiteName || !currentSuite) {
      return;
    }

    const allVariables = {
      ...templateVariables,
      ...(userMessage.trim() ? { user_message: userMessage.trim() } : {})
    };

    const newTest: UnitTestDefinition = {
      name: testName.trim(),
      description: description.trim() || undefined,
      test_suite_name: testSuiteName,
      prompt_reference: promptReference.trim(),
      template_variables: allVariables,
      expected_output: expectedOutput.trim() || null,
      metrics,
      enabled: true,
    };

    // Add test to current suite
    const updatedSuite = {
      ...currentSuite,
      test_suite: {
        ...currentSuite.test_suite,
        tests: [...currentSuite.test_suite.tests, newTest],
      },
    };

    await saveTestSuite(repoName, updatedSuite);
    router.push(`/tests/${encodeURIComponent(testSuiteName)}?repo_name=${encodeURIComponent(repoName)}`);
  };

  const handleBack = () => {
    router.push(`/tests?repo_name=${encodeURIComponent(repoName || '')}`);
  };

  if (!repoName) {
    return (
      <Box height="100vh" display="flex" alignItems="center" justifyContent="center">
        <Text>No repository selected</Text>
      </Box>
    );
  }

  const canSave = testName.trim() && testSuiteName && promptReference.trim() && userMessage.trim();

  return (
    <Box height="100vh" width="100%" display="flex" flexDirection="column">
      {/* Header */}
      <Box py={4} px={6} position="sticky" top={0} zIndex={10} bg="bg.subtle" borderBottomWidth="1px">
        <HStack justify="space-between" align="center">
          <HStack gap={4}>
            <Button variant="outline" onClick={handleBack} size="sm">
              <HStack gap={2}>
                <LuArrowLeft size={16} />
                <Text>Back</Text>
              </HStack>
            </Button>
            <VStack align="start" gap={1}>
              <Text color="fg.muted" fontSize="2xl" letterSpacing="tight" fontWeight="1000">
                Create New Test
              </Text>
              <Text fontSize="sm" opacity={0.7}>
                Configure test parameters and assign to a test suite
              </Text>
            </VStack>
          </HStack>
          <Button onClick={handleSave} disabled={!canSave || isLoading} loading={isLoading}>
            <LuSave /> {isLoading ? 'Saving...' : 'Save Test'}
          </Button>
        </HStack>
      </Box>

      <ScrollArea.Root flex="1" width="100%">
        <ScrollArea.Viewport>
          <ScrollArea.Content>
            <Container maxW="4xl" py={6}>
              <VStack align="stretch" gap={6}>
                {/* Basic Information */}
                <Card.Root>
                  <Card.Header>
                    <Heading size="md">Basic Information</Heading>
                  </Card.Header>
                  <Card.Body>
                    <VStack align="stretch" gap={4}>
                      <Field.Root required>
                        <Field.Label>Test Name</Field.Label>
                        <Input
                          value={testName}
                          onChange={(e) => setTestName(e.target.value)}
                          placeholder="test-answer-relevancy"
                        />
                        <Field.HelperText>Unique identifier for this test</Field.HelperText>
                      </Field.Root>

                      <Field.Root>
                        <Field.Label>Description</Field.Label>
                        <Textarea
                          value={description}
                          onChange={(e) => setDescription(e.target.value)}
                          placeholder="Describe what this test validates..."
                          rows={2}
                        />
                      </Field.Root>

                      <Field.Root required>
                        <Field.Label>Test Suite</Field.Label>
                        <select
                          value={testSuiteName}
                          onChange={(e) => setTestSuiteName(e.target.value)}
                          style={{ 
                            width: '100%', 
                            padding: '0.5rem', 
                            borderRadius: '0.375rem',
                            borderWidth: '1px',
                            borderColor: 'var(--chakra-colors-border-default)'
                          }}
                        >
                          <option value="">Select a test suite</option>
                          {testSuites.map((suite) => (
                            <option key={suite.name} value={suite.name}>
                              {suite.name} ({suite.test_count} tests)
                            </option>
                          ))}
                        </select>
                        <Field.HelperText>
                          The test suite this test belongs to
                        </Field.HelperText>
                      </Field.Root>

                      <Field.Root required>
                        <Field.Label>Prompt Reference</Field.Label>
                        <PromptSelector
                          repoName={repoName}
                          value={promptReference}
                          onChange={handlePromptSelection}
                        />
                      </Field.Root>

                      <Field.Root required>
                        <Field.Label>User Message</Field.Label>
                        <Textarea
                          value={userMessage}
                          onChange={(e) => setUserMessage(e.target.value)}
                          placeholder="What do you want to ask the prompt?"
                          rows={3}
                        />
                        <Field.HelperText>
                          The message/input to send to the prompt for evaluation
                        </Field.HelperText>
                      </Field.Root>
                    </VStack>
                  </Card.Body>
                </Card.Root>

                {/* Template Variables Section */}
                <Card.Root>
                  <Card.Header>
                    <Heading size="md">Template Variables</Heading>
                  </Card.Header>
                  <Card.Body>
                    <TemplateVariableEditor
                      variables={templateVariables}
                      onChange={setTemplateVariables}
                    />
                  </Card.Body>
                </Card.Root>

                {/* Metrics & Expected Output Section */}
                <Card.Root>
                  <Card.Header>
                    <Heading size="md">Metrics & Expected Output</Heading>
                  </Card.Header>
                  <Card.Body>
                    <VStack align="stretch" gap={4}>
                      <Field.Root>
                        <Field.Label>Expected Output (Optional)</Field.Label>
                        <Textarea
                          value={expectedOutput}
                          onChange={(e) => setExpectedOutput(e.target.value)}
                          placeholder="The expected response from the prompt..."
                          rows={4}
                        />
                        <Field.HelperText>
                          Used for comparison metrics like faithfulness
                        </Field.HelperText>
                      </Field.Root>

                      <Box>
                        <Text fontWeight="semibold" mb={2}>Evaluation Metrics</Text>
                        <MetricSelector metrics={metrics} onChange={setMetrics} />
                      </Box>
                    </VStack>
                  </Card.Body>
                </Card.Root>
              </VStack>
            </Container>
          </ScrollArea.Content>
        </ScrollArea.Viewport>
        <ScrollArea.Scrollbar orientation="vertical">
          <ScrollArea.Thumb />
        </ScrollArea.Scrollbar>
      </ScrollArea.Root>
    </Box>
  );
}

export default function TestCreatePage() {
  return (
    <Suspense fallback={<LoadingOverlay isVisible={true} title="Loading..." subtitle="Loading test creation" />}>
      <TestCreatePageContent />
    </Suspense>
  );
}