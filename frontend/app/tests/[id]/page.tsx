'use client';

import { useEffect, useState } from 'react';
import { useParams, useSearchParams, useRouter } from 'next/navigation';
import {
  VStack,
  HStack,
  Box,
  ScrollArea,
  Spinner,
  Text,
  Button,
  IconButton,
  Collapsible,
  Card,
  Fieldset,
  Stack,
} from '@chakra-ui/react';
import { FaTrash, FaPlus } from 'react-icons/fa';
import { LuChevronDown, LuChevronUp } from 'react-icons/lu';
import { LuArrowLeft } from 'react-icons/lu';
import { useTestStore } from '@/stores/testStore/testStore';
import { useSelectedRepository } from '@/stores/repositoryFilterStore';
import { TestSuiteEditor } from '@/components/tests/TestSuiteEditor';
import { UnitTestList } from '@/components/tests/UnitTestList';
import { TestExecutor } from '@/components/tests/TestExecutor';
import { TestResults } from '@/components/tests/TestResults';
import { UnitTestEditor } from '@/components/tests/UnitTestEditor';
import type { UnitTestDefinition } from '@/types/test';

export default function TestSuiteDetailPage() {
  const params = useParams();
  const searchParams = useSearchParams();
  const router = useRouter();
  
  const suiteName = decodeURIComponent(params.id as string);
  const selectedRepository = useSelectedRepository();
  const repoName = searchParams.get('repo_name') || selectedRepository;
  const isNewSuite = suiteName === 'new';
  
  const [editingTest, setEditingTest] = useState<UnitTestDefinition | null>(null);
  const [isEditorOpen, setIsEditorOpen] = useState(false);
  const [isTestsListOpen, setIsTestsListOpen] = useState(true);
  
  // Store state
  const currentSuite = useTestStore((state) => state.currentSuite);
  const currentExecution = useTestStore((state) => state.currentExecution);
  const isLoading = useTestStore((state) => state.isLoading);
  const error = useTestStore((state) => state.error);
  
  // Store actions
  const fetchTestSuite = useTestStore((state) => state.fetchTestSuite);
  const saveTestSuite = useTestStore((state) => state.saveTestSuite);
  const deleteTestSuite = useTestStore((state) => state.deleteTestSuite);
  const executeTestSuite = useTestStore((state) => state.executeTestSuite);
  const fetchLatestExecution = useTestStore((state) => state.fetchLatestExecution);
  const setCurrentSuite = useTestStore((state) => state.setCurrentSuite);

  // Initialize or fetch test suite on mount
  useEffect(() => {
    if (typeof window !== 'undefined' && repoName) {
      if (isNewSuite) {
        // Initialize empty test suite for new creation
        const now = new Date().toISOString();
        setCurrentSuite({
          test_suite: {
            name: '',
            description: '',
            tests: [],
            tags: [],
            created_at: now,
            updated_at: now,
          },
        });
      } else if (suiteName) {
        // Fetch existing test suite
        fetchTestSuite(repoName, suiteName);
        fetchLatestExecution(repoName, suiteName);
      }
    }
  }, [repoName, suiteName, isNewSuite, fetchTestSuite, fetchLatestExecution, setCurrentSuite]);

  const handleBack = () => {
    router.push(`/tests?repo_name=${encodeURIComponent(repoName || '')}`);
  };

  const handleSave = async () => {
    if (currentSuite && repoName) {
      await saveTestSuite(repoName, currentSuite);
    }
  };

  const handleDelete = async () => {
    if (repoName && suiteName && confirm(`Are you sure you want to delete test suite "${suiteName}"?`)) {
      await deleteTestSuite(repoName, suiteName);
      router.push(`/tests?repo_name=${encodeURIComponent(repoName)}`);
    }
  };

  const handleExecute = async () => {
    if (repoName && suiteName) {
      await executeTestSuite(repoName, suiteName);
    }
  };

  if (isLoading && !currentSuite) {
    return (
      <Box height="100vh" display="flex" alignItems="center" justifyContent="center">
        <VStack gap={4}>
          <Spinner size="xl" />
          <Text>Loading test suite...</Text>
        </VStack>
      </Box>
    );
  }

  if (error) {
    return (
      <Box height="100vh" display="flex" alignItems="center" justifyContent="center">
        <VStack gap={4}>
          <Text color="red.500" fontSize="lg">{error}</Text>
          <Button onClick={handleBack}>Go Back</Button>
        </VStack>
      </Box>
    );
  }

  if (!currentSuite) {
    return (
      <Box height="100vh" display="flex" alignItems="center" justifyContent="center">
        <VStack gap={4}>
          <Text fontSize="lg">Test suite not found</Text>
          <Button onClick={handleBack}>Go Back</Button>
        </VStack>
      </Box>
    );
  }

  return (
    <Box height="100vh" width="100%" display="flex" flexDirection="column">
      {/* Header */}
      <Box py={4} px={6} position="sticky" top={0} zIndex={10} bg="bg.subtle">
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
                {currentSuite.test_suite.name || 'New Test Suite'}
              </Text>
              <Text fontSize="sm" opacity={0.7}>
                Edit test suite configuration and manage tests. Click Save to persist changes.
              </Text>
            </VStack>
          </HStack>
          <HStack gap={3}>
            <Button onClick={handleSave} disabled={isLoading} loading={isLoading}>
              {isLoading ? 'Saving...' : 'Save Test Suite'}
            </Button>
            <IconButton
              aria-label="Delete test suite"
              colorScheme="red"
              variant="ghost"
              onClick={handleDelete}
            >
              <FaTrash />
            </IconButton>
          </HStack>
        </HStack>
      </Box>

      <ScrollArea.Root flex="1" width="100%">
        <ScrollArea.Viewport
          css={{
            "--scroll-shadow-size": "5rem",
            maskImage:
              "linear-gradient(#000,#000,transparent 0,#000 var(--scroll-shadow-size),#000 calc(100% - var(--scroll-shadow-size)),transparent)",
            "&[data-at-top]": {
              maskImage:
                "linear-gradient(180deg,#000 calc(100% - var(--scroll-shadow-size)),transparent)",
            },
            "&[data-at-bottom]": {
              maskImage:
                "linear-gradient(0deg,#000 calc(100% - var(--scroll-shadow-size)),transparent)",
            },
          }}
        >
          <ScrollArea.Content>
            <Box position="relative">
              {/* Main Content - Two column split layout */}
              <Box p={6}>
                <HStack gap={6} align="start" minH="600px">
                  {/* Left Section - Test Suite Info & Tests List */}
                  <Box width="40%">
                    <VStack gap={6} align="stretch">
                      {/* Test Suite Editor */}
                      <TestSuiteEditor
                        suite={currentSuite.test_suite}
                        onChange={(updated) => {
                          setCurrentSuite({ test_suite: updated });
                        }}
                      />

                      {/* Unit Tests List */}
                      <Card.Root>
                        <Card.Body>
                          <Fieldset.Root>
                            <HStack justify="space-between" align="center">
                              <Stack flex={1}>
                                <Fieldset.Legend>Tests</Fieldset.Legend>
                                <Fieldset.HelperText color="text.tertiary">
                                  Add and manage unit tests for this test suite
                                </Fieldset.HelperText>
                              </Stack>
                              <HStack gap={2}>
                                <Button
                                  size="sm"
                                  onClick={() => {
                                    setEditingTest(null);
                                    setIsEditorOpen(true);
                                  }}
                                >
                                  <FaPlus /> Add Test
                                </Button>
                                <Button
                                  variant="ghost"
                                  _hover={{ bg: "bg.subtle" }}
                                  size="sm"
                                  onClick={() => setIsTestsListOpen(!isTestsListOpen)}
                                  aria-label={isTestsListOpen ? "Collapse tests list" : "Expand tests list"}
                                >
                                  <HStack gap={1}>
                                    <Text fontSize="xs" fontWeight="medium">
                                      {isTestsListOpen ? "Hide" : "Show"}
                                    </Text>
                                    {isTestsListOpen ? <LuChevronUp /> : <LuChevronDown />}
                                  </HStack>
                                </Button>
                              </HStack>
                            </HStack>

                            <Fieldset.Content>
                              <Collapsible.Root open={isTestsListOpen}>
                                <Collapsible.Content>
                                  <Box mt={3}>
                              <UnitTestList
                                tests={currentSuite.test_suite.tests || []}
                                onEdit={(testName) => {
                                  const test = currentSuite.test_suite.tests?.find(t => t.name === testName);
                                  if (test) {
                                    setEditingTest(test);
                                    setIsEditorOpen(true);
                                  }
                                }}
                                onDelete={(testName) => {
                                  if (confirm(`Delete test "${testName}"?`)) {
                                    const updatedTests = currentSuite.test_suite.tests?.filter(t => t.name !== testName) || [];
                                    setCurrentSuite({
                                      test_suite: {
                                        ...currentSuite.test_suite,
                                        tests: updatedTests,
                                      },
                                    });
                                  }
                                }}
                                onRun={(testName) => {
                                  if (repoName) {
                                    executeTestSuite(repoName, suiteName, [testName]);
                                  }
                                }}
                                onToggleEnabled={(testName, enabled) => {
                                  const updatedTests = currentSuite.test_suite.tests?.map(t =>
                                    t.name === testName ? { ...t, enabled } : t
                                  );
                                  setCurrentSuite({
                                    test_suite: {
                                      ...currentSuite.test_suite,
                                      tests: updatedTests,
                                    },
                                  });
                                }}
                              />
                                  </Box>
                                </Collapsible.Content>
                              </Collapsible.Root>
                            </Fieldset.Content>
                          </Fieldset.Root>
                        </Card.Body>
                      </Card.Root>
                    </VStack>
                  </Box>

                  {/* Right Section - Test Executor & Results */}
                  <Box width="60%">
                    <VStack gap={6} align="stretch">
                      {/* Test Executor */}
                      <TestExecutor
                        repoName={repoName || ''}
                        suiteName={suiteName}
                        tests={currentSuite.test_suite.tests || []}
                        onExecute={executeTestSuite}
                        isExecuting={isLoading}
                      />

                      {/* Test Results */}
                      {currentExecution && (
                        <TestResults execution={currentExecution} />
                      )}
                    </VStack>
                  </Box>
                </HStack>
              </Box>
            </Box>
          </ScrollArea.Content>
        </ScrollArea.Viewport>
        <ScrollArea.Scrollbar orientation="vertical">
          <ScrollArea.Thumb />
        </ScrollArea.Scrollbar>
      </ScrollArea.Root>

      {/* Unit Test Editor Dialog */}
      <UnitTestEditor
        open={isEditorOpen}
        onOpenChange={setIsEditorOpen}
        test={editingTest}
        repoName={repoName || ''}
        suiteMetrics={currentSuite.test_suite.metrics || []}
        onSave={(test) => {
          const isNew = !currentSuite.test_suite.tests?.find(t => t.name === editingTest?.name);
          const updatedTests = isNew
            ? [...(currentSuite.test_suite.tests || []), test]
            : currentSuite.test_suite.tests?.map(t =>
                t.name === editingTest?.name ? test : t
              );
          
          setCurrentSuite({
            test_suite: {
              ...currentSuite.test_suite,
              tests: updatedTests,
            },
          });
          setIsEditorOpen(false);
          setEditingTest(null);
        }}
      />
    </Box>
  );
}