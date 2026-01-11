'use client';

import { useEffect, useState } from 'react';
import { useParams, usePathname, useRouter } from 'next/navigation';
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
import { useEvalStore } from '@/stores/evalStore';
import { EvalEditor } from '@/components/evals/EvalEditor';
import { TestList } from '@/components/evals/TestList';
import { EvalExecutor } from '@/components/evals/EvalExecutor';
import { EvalExecutionHistory } from '@/components/evals/EvalExecutionHistory';
import { TestEditor } from '@/components/evals/TestEditor';
import { errorNotification } from '@/lib/notifications';
import { decodeBase64Url, buildEvalEditorUrl } from '@/lib/urlEncoder';
import { toaster } from '@/components/ui/toaster';

export default function EvalEditorPage() {
  const params = useParams();
  const pathname = usePathname();
  const router = useRouter();
  
  // Parse base64-encoded URL parameters
  const pathParts = pathname.split('/').filter(Boolean);
  const encodedRepo = pathParts[2]; // /evals/editor/{base64_repo}/...
  const encodedEvalId = pathParts[3]; // /evals/editor/{base64_repo}/{base64_eval_id}
  
  const repoName = encodedRepo ? decodeBase64Url(encodedRepo) : '';
  // Check if it's 'new' BEFORE decoding to avoid decoding the literal string 'new'
  const isNewEval = encodedEvalId === 'new';
  const filePath = isNewEval ? 'new' : (encodedEvalId ? decodeBase64Url(encodedEvalId) : '');
  
  const [isEditorOpen, setIsEditorOpen] = useState(false);
  const [isTestsListOpen, setIsTestsListOpen] = useState(true);
  
  // Store state
  const currentEval = useEvalStore((state) => state.currentEval);
  const executionHistory = useEvalStore((state) => state.executionHistory);
  const editingTest = useEvalStore((state) => state.editingTest);
  const isLoading = useEvalStore((state) => state.isLoading);
  const error = useEvalStore((state) => state.error);

  // Store actions
  const fetchEval = useEvalStore((state) => state.fetchEval);
  const saveEval = useEvalStore((state) => state.saveEval);
  const deleteEval = useEvalStore((state) => state.deleteEval);
  const executeEval = useEvalStore((state) => state.executeEval);
  const fetchExecutionHistory = useEvalStore((state) => state.fetchExecutionHistory);
  const setCurrentEval = useEvalStore((state) => state.setCurrentEval);
  const setEditingTest = useEvalStore((state) => state.setEditingTest);

  // Initialize or fetch eval on mount
  useEffect(() => {
    if (typeof window !== 'undefined' && repoName) {
      if (isNewEval) {
        // Initialize empty eval for new creation
        const now = new Date().toISOString();
        setCurrentEval({
          eval: {
            name: '',
            description: '',
            tests: [],
            tags: [],
            created_at: now,
            updated_at: now,
          },
        });
      } else if (filePath) {
        // Fetch existing eval and last 3 executions
        fetchEval(repoName, filePath);
        fetchExecutionHistory(repoName, filePath, 3);
      }
    }
  }, [repoName, filePath, isNewEval, fetchEval, fetchExecutionHistory, setCurrentEval]);

  const handleBack = () => {
    router.push('/evals');
  };

  const handleSave = async () => {
    if (!currentEval || !repoName) return;

    // Use 'new' for new evals, or the existing filePath for updates
    const pathToSave = isNewEval ? 'new' : filePath;

    const savePromise = saveEval(repoName, currentEval, pathToSave);

    toaster.promise(savePromise, {
      loading: {
        title: 'Saving...',
        description: 'Creating a PR for your changes.',
      },
      success: (data) => {
        const prInfo = data?.pr_info as { pr_url?: string; pr_number?: number } | null | undefined;
        const prUrl = prInfo?.pr_url;
        const prNumber = prInfo?.pr_number;

        // If we're creating a new eval, redirect to the actual eval page using the file_path
        if (isNewEval && data?.file_path) {
          setTimeout(() => {
            router.push(buildEvalEditorUrl(repoName, data.file_path));
          }, 100);
        }

        if (prUrl) {
          return {
            title: 'Successfully saved!',
            description: `Pull Request #${prNumber} created`,
            duration: 30000, // Sticky notification - 30 seconds
            closable: true,
            action: {
              label: 'View PR',
              onClick: () => {
                window.open(prUrl, '_blank', 'noopener,noreferrer');
              },
            },
          };
        }

        return {
          title: 'Successfully saved!',
          description: 'Changes committed successfully',
          duration: 5000, // Auto-dismiss after 5 seconds
          closable: true,
        };
      },
      error: {
        title: 'Save failed',
        description: 'Something went wrong while saving',
      },
    });
  };

  const handleDelete = async () => {
    if (repoName && filePath && confirm(`Are you sure you want to delete this eval?`)) {
      await deleteEval(repoName, filePath);
      router.push('/evals');
    }
  };

  const handleExecute = async () => {
    if (repoName && filePath) {
      await executeEval(repoName, filePath);
    }
  };

  if (isLoading && !currentEval) {
    return (
      <Box height="100vh" display="flex" alignItems="center" justifyContent="center">
        <VStack gap={4}>
          <Spinner size="xl" />
          <Text>Loading eval...</Text>
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

  if (!currentEval) {
    return (
      <Box height="100vh" display="flex" alignItems="center" justifyContent="center">
        <VStack gap={4}>
          <Text fontSize="lg">Eval not found</Text>
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
                {currentEval.eval.name || 'New Eval'}
              </Text>
              <Text fontSize="sm" opacity={0.7}>
                Edit eval configuration and manage tests. Click Save to persist changes.
              </Text>
            </VStack>
          </HStack>
          <HStack gap={3}>
            <Button onClick={handleSave} disabled={isLoading} loading={isLoading}>
              {isLoading ? 'Saving...' : 'Save Eval'}
            </Button>
            <IconButton
              aria-label="Delete eval"
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
                  {/* Left Section - Eval Info & Tests List */}
                  <Box width="40%">
                    <VStack gap={6} align="stretch">
                      {/* Eval Editor */}
                      <EvalEditor
                        eval={currentEval.eval}
                        onChange={(updated) => {
                          setCurrentEval({ eval: updated });
                        }}
                      />

                      {/* Tests List */}
                      <Card.Root>
                        <Card.Body>
                          <Fieldset.Root>
                            <HStack justify="space-between" align="center">
                              <Stack flex={1}>
                                <Fieldset.Legend>Tests</Fieldset.Legend>
                                <Fieldset.HelperText color="text.tertiary">
                                  Add and manage tests for this eval
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
                              <TestList
                                tests={currentEval.eval.tests || []}
                                onEdit={(testName) => {
                                  const testItem = currentEval.eval.tests?.find(t => t.name === testName);
                                  if (testItem) {
                                    setEditingTest(testItem);
                                    setIsEditorOpen(true);
                                  }
                                }}
                                onDelete={async (testName) => {
                                  if (confirm(`Delete test "${testName}"?`)) {
                                    const updatedTests = currentEval.eval.tests?.filter(t => t.name !== testName) || [];
                                    const updatedEval = {
                                      eval: {
                                        ...currentEval.eval,
                                        tests: updatedTests,
                                      },
                                    };
                                    setCurrentEval(updatedEval);

                                    // Save the changes to backend with toast notification
                                    if (repoName && !isNewEval) {
                                      const savePromise = saveEval(repoName, updatedEval, filePath);

                                      toaster.promise(savePromise, {
                                        loading: {
                                          title: 'Deleting test...',
                                          description: 'Creating a PR for your changes.',
                                        },
                                        success: (data) => {
                                          const prInfo = data?.pr_info as { pr_url?: string; pr_number?: number } | null | undefined;
                                          const prUrl = prInfo?.pr_url;
                                          const prNumber = prInfo?.pr_number;

                                          if (prUrl) {
                                            return {
                                              title: 'Test deleted!',
                                              description: `Pull Request #${prNumber} created`,
                                              duration: 30000,
                                              closable: true,
                                              action: {
                                                label: 'View PR',
                                                onClick: () => {
                                                  window.open(prUrl, '_blank', 'noopener,noreferrer');
                                                },
                                              },
                                            };
                                          }

                                          return {
                                            title: 'Test deleted!',
                                            description: 'Changes committed successfully',
                                            duration: 5000,
                                            closable: true,
                                          };
                                        },
                                        error: (error) => {
                                          // Revert the local change if save fails
                                          setCurrentEval(currentEval);
                                          return {
                                            title: 'Delete failed',
                                            description: 'Failed to delete test. Please try again.',
                                          };
                                        },
                                      });
                                    }
                                  }
                                }}
                                onRun={(testName) => {
                                  if (repoName) {
                                    executeEval(repoName, filePath, [testName]);
                                  }
                                }}
                                onToggleEnabled={(testName, enabled) => {
                                  const updatedTests = currentEval.eval.tests?.map(t =>
                                    t.name === testName ? { ...t, enabled } : t
                                  );
                                  setCurrentEval({
                                    eval: {
                                      ...currentEval.eval,
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

                  {/* Right Section - Eval Executor & Results */}
                  <Box width="60%">
                    <VStack gap={6} align="stretch">
                      {/* Eval Executor */}
                      <EvalExecutor
                        repoName={repoName || ''}
                        filePath={filePath}
                        tests={currentEval.eval.tests || []}
                        onExecute={executeEval}
                        isExecuting={isLoading}
                      />

                      {/* Eval Execution History - Show all executions in one panel */}
                      <EvalExecutionHistory executions={executionHistory} />
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

      {/* Test Editor Dialog */}
      <TestEditor
        open={isEditorOpen}
        onOpenChange={setIsEditorOpen}
        testItem={editingTest}
        repoName={repoName || ''}
        evalMetrics={currentEval.eval.metrics || []}
        onSave={(testItem) => {
          const isNew = !currentEval.eval.tests?.find(t => t.name === editingTest?.name);
          const updatedTests = isNew
            ? [...(currentEval.eval.tests || []), testItem]
            : currentEval.eval.tests?.map(t =>
                t.name === editingTest?.name ? testItem : t
              );
          
          setCurrentEval({
            eval: {
              ...currentEval.eval,
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