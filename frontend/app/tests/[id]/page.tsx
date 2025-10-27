'use client';

import { useEffect, useState } from 'react';
import { useParams, useSearchParams, useRouter } from 'next/navigation';
import {
  VStack,
  HStack,
  Box,
  Container,
  ScrollArea,
  Spinner,
  Text,
  Button,
  IconButton,
  Heading,
  Badge,
} from '@chakra-ui/react';
import { FaArrowLeft, FaSave, FaTrash, FaPlus } from 'react-icons/fa';
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
      <Box borderBottomWidth="1px" borderBottomColor="border" py={4} px={6} bg="bg.panel">
        <Container maxW="7xl">
          <HStack justify="space-between">
            <HStack gap={4}>
              <IconButton
                aria-label="Go back"
                onClick={handleBack}
                size="sm"
                variant="ghost"
              >
                <FaArrowLeft />
              </IconButton>
              <VStack align="start" gap={1}>
                <Heading size="lg">{currentSuite.test_suite.name}</Heading>
                {currentSuite.test_suite.description && (
                  <Text fontSize="sm" color="fg.subtle">
                    {currentSuite.test_suite.description}
                  </Text>
                )}
              </VStack>
              <Badge colorScheme="blue">
                {currentSuite.test_suite.tests.length} tests
              </Badge>
            </HStack>
            
            <HStack gap={2}>
              <Button
                colorScheme="blue"
                onClick={handleSave}
                loading={isLoading}
              >
                <FaSave /> Save
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
        </Container>
      </Box>

      <ScrollArea.Root flex="1" width="100%">
        <ScrollArea.Viewport>
          <ScrollArea.Content>
            <Container maxW="7xl" py={6}>
              <VStack gap={6} align="stretch">
                {/* Test Suite Editor */}
                <TestSuiteEditor
                  suite={currentSuite.test_suite}
                  onChange={(updated) => {
                    setCurrentSuite({ test_suite: updated });
                  }}
                />

                {/* Test Executor & Results */}
                <TestExecutor
                  repoName={repoName || ''}
                  suiteName={suiteName}
                  tests={currentSuite.test_suite.tests}
                  onExecute={executeTestSuite}
                  isExecuting={isLoading}
                />

                {currentExecution && (
                  <TestResults execution={currentExecution} />
                )}

                {/* Unit Tests List */}
                <Box>
                  <HStack justify="space-between" mb={4}>
                    <Heading size="md">Tests</Heading>
                    <Button
                      colorScheme="blue"
                      size="sm"
                      onClick={() => {
                        setEditingTest(null);
                        setIsEditorOpen(true);
                      }}
                    >
                      <FaPlus /> Add Test
                    </Button>
                  </HStack>
                  <UnitTestList
                    tests={currentSuite.test_suite.tests}
                    onEdit={(testName) => {
                      const test = currentSuite.test_suite.tests.find(t => t.name === testName);
                      if (test) {
                        setEditingTest(test);
                        setIsEditorOpen(true);
                      }
                    }}
                    onDelete={(testName) => {
                      if (confirm(`Delete test "${testName}"?`)) {
                        const updatedTests = currentSuite.test_suite.tests.filter(t => t.name !== testName);
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
                      const updatedTests = currentSuite.test_suite.tests.map(t =>
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

                {/* Unit Test Editor Dialog */}
                <UnitTestEditor
                  open={isEditorOpen}
                  onOpenChange={setIsEditorOpen}
                  test={editingTest}
                  repoName={repoName || ''}
                  onSave={(test) => {
                    const isNew = !currentSuite.test_suite.tests.find(t => t.name === editingTest?.name);
                    const updatedTests = isNew
                      ? [...currentSuite.test_suite.tests, test]
                      : currentSuite.test_suite.tests.map(t =>
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