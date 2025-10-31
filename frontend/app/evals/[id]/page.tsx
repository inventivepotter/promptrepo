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
import { useEvalStore } from '@/stores/evalStore';
import { useSelectedRepository } from '@/stores/repositoryFilterStore';
import { EvalSuiteEditor } from '@/components/evals/EvalSuiteEditor';
import { EvalList } from '@/components/evals/EvalList';
import { EvalExecutor } from '@/components/evals/EvalExecutor';
import { EvalResults } from '@/components/evals/EvalResults';
import { EvalEditor } from '@/components/evals/EvalEditor';
import { errorNotification } from '@/lib/notifications';
import type { EvalDefinition } from '@/types/eval';

export default function EvalSuiteDetailPage() {
  const params = useParams();
  const searchParams = useSearchParams();
  const router = useRouter();
  
  const suiteName = decodeURIComponent(params.id as string);
  const selectedRepository = useSelectedRepository();
  const repoName = searchParams.get('repo_name') || selectedRepository;
  const isNewSuite = suiteName === 'new';
  
  const [isEditorOpen, setIsEditorOpen] = useState(false);
  const [isTestsListOpen, setIsTestsListOpen] = useState(true);
  
  // Store state
  const currentSuite = useEvalStore((state) => state.currentSuite);
  const currentExecution = useEvalStore((state) => state.currentExecution);
  const editingEval = useEvalStore((state) => state.editingEval);
  const isLoading = useEvalStore((state) => state.isLoading);
  const error = useEvalStore((state) => state.error);
  
  // Store actions
  const fetchEvalSuite = useEvalStore((state) => state.fetchEvalSuite);
  const saveEvalSuite = useEvalStore((state) => state.saveEvalSuite);
  const deleteEvalSuite = useEvalStore((state) => state.deleteEvalSuite);
  const executeEvalSuite = useEvalStore((state) => state.executeEvalSuite);
  const fetchLatestExecution = useEvalStore((state) => state.fetchLatestExecution);
  const setCurrentSuite = useEvalStore((state) => state.setCurrentSuite);
  const setEditingEval = useEvalStore((state) => state.setEditingEval);

  // Initialize or fetch eval suite on mount
  useEffect(() => {
    if (typeof window !== 'undefined' && repoName) {
      if (isNewSuite) {
        // Initialize empty eval suite for new creation
        const now = new Date().toISOString();
        setCurrentSuite({
          eval_suite: {
            name: '',
            description: '',
            evals: [],
            tags: [],
            created_at: now,
            updated_at: now,
          },
        });
      } else if (suiteName) {
        // Fetch existing eval suite
        fetchEvalSuite(repoName, suiteName);
        fetchLatestExecution(repoName, suiteName);
      }
    }
  }, [repoName, suiteName, isNewSuite, fetchEvalSuite, fetchLatestExecution, setCurrentSuite]);

  const handleBack = () => {
    router.push(`/evals?repo_name=${encodeURIComponent(repoName || '')}`);
  };

  const handleSave = async () => {
    if (currentSuite && repoName) {
      await saveEvalSuite(repoName, currentSuite);
      
      // If we're creating a new suite, redirect to the actual suite page
      if (isNewSuite && currentSuite.eval_suite.name) {
        router.push(`/evals/${encodeURIComponent(currentSuite.eval_suite.name)}?repo_name=${encodeURIComponent(repoName)}`);
      }
    }
  };

  const handleDelete = async () => {
    if (repoName && suiteName && confirm(`Are you sure you want to delete eval suite "${suiteName}"?`)) {
      await deleteEvalSuite(repoName, suiteName);
      router.push(`/evals?repo_name=${encodeURIComponent(repoName)}`);
    }
  };

  const handleExecute = async () => {
    if (repoName && suiteName) {
      await executeEvalSuite(repoName, suiteName);
    }
  };

  if (isLoading && !currentSuite) {
    return (
      <Box height="100vh" display="flex" alignItems="center" justifyContent="center">
        <VStack gap={4}>
          <Spinner size="xl" />
          <Text>Loading eval suite...</Text>
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
          <Text fontSize="lg">Eval suite not found</Text>
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
                {currentSuite.eval_suite.name || 'New Eval Suite'}
              </Text>
              <Text fontSize="sm" opacity={0.7}>
                Edit eval suite configuration and manage evals. Click Save to persist changes.
              </Text>
            </VStack>
          </HStack>
          <HStack gap={3}>
            <Button onClick={handleSave} disabled={isLoading} loading={isLoading}>
              {isLoading ? 'Saving...' : 'Save Eval Suite'}
            </Button>
            <IconButton
              aria-label="Delete eval suite"
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
                  {/* Left Section - Eval Suite Info & Evals List */}
                  <Box width="40%">
                    <VStack gap={6} align="stretch">
                      {/* Eval Suite Editor */}
                      <EvalSuiteEditor
                        suite={currentSuite.eval_suite}
                        onChange={(updated) => {
                          setCurrentSuite({ eval_suite: updated });
                        }}
                      />

                      {/* Evals List */}
                      <Card.Root>
                        <Card.Body>
                          <Fieldset.Root>
                            <HStack justify="space-between" align="center">
                              <Stack flex={1}>
                                <Fieldset.Legend>Evals</Fieldset.Legend>
                                <Fieldset.HelperText color="text.tertiary">
                                  Add and manage evals for this eval suite
                                </Fieldset.HelperText>
                              </Stack>
                              <HStack gap={2}>
                                <Button
                                  size="sm"
                                  onClick={() => {
                                    setEditingEval(null);
                                    setIsEditorOpen(true);
                                  }}
                                >
                                  <FaPlus /> Add Eval
                                </Button>
                                <Button
                                  variant="ghost"
                                  _hover={{ bg: "bg.subtle" }}
                                  size="sm"
                                  onClick={() => setIsTestsListOpen(!isTestsListOpen)}
                                  aria-label={isTestsListOpen ? "Collapse evals list" : "Expand evals list"}
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
                              <EvalList
                                evals={currentSuite.eval_suite.evals || []}
                                onEdit={(evalName) => {
                                  const evalItem = currentSuite.eval_suite.evals?.find(e => e.name === evalName);
                                  if (evalItem) {
                                    setEditingEval(evalItem);
                                    setIsEditorOpen(true);
                                  }
                                }}
                                onDelete={async (evalName) => {
                                  if (confirm(`Delete eval "${evalName}"?`)) {
                                    const updatedEvals = currentSuite.eval_suite.evals?.filter(e => e.name !== evalName) || [];
                                    const updatedSuite = {
                                      eval_suite: {
                                        ...currentSuite.eval_suite,
                                        evals: updatedEvals,
                                      },
                                    };
                                    setCurrentSuite(updatedSuite);

                                    // Save the changes to backend
                                    if (repoName) {
                                      try {
                                        await saveEvalSuite(repoName, updatedSuite);
                                      } catch (error) {
                                        console.error('Failed to save eval suite after delete:', error);
                                        // Revert the local change if save fails
                                        setCurrentSuite(currentSuite);
                                        errorNotification('Save Failed', 'Failed to delete eval. Please try again.');
                                      }
                                    }
                                  }
                                }}
                                onRun={(evalName) => {
                                  if (repoName) {
                                    executeEvalSuite(repoName, suiteName, [evalName]);
                                  }
                                }}
                                onToggleEnabled={(evalName, enabled) => {
                                  const updatedEvals = currentSuite.eval_suite.evals?.map(e =>
                                    e.name === evalName ? { ...e, enabled } : e
                                  );
                                  setCurrentSuite({
                                    eval_suite: {
                                      ...currentSuite.eval_suite,
                                      evals: updatedEvals,
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
                        suiteName={suiteName}
                        evals={currentSuite.eval_suite.evals || []}
                        onExecute={executeEvalSuite}
                        isExecuting={isLoading}
                      />

                      {/* Eval Results */}
                      {currentExecution && (
                        <EvalResults execution={currentExecution} />
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

      {/* Eval Editor Dialog */}
      <EvalEditor
        open={isEditorOpen}
        onOpenChange={setIsEditorOpen}
        evalItem={editingEval}
        repoName={repoName || ''}
        suiteMetrics={currentSuite.eval_suite.metrics || []}
        onSave={(evalItem) => {
          const isNew = !currentSuite.eval_suite.evals?.find(e => e.name === editingEval?.name);
          const updatedEvals = isNew
            ? [...(currentSuite.eval_suite.evals || []), evalItem]
            : currentSuite.eval_suite.evals?.map(e =>
                e.name === editingEval?.name ? evalItem : e
              );
          
          setCurrentSuite({
            eval_suite: {
              ...currentSuite.eval_suite,
              evals: updatedEvals,
            },
          });
          setIsEditorOpen(false);
          setEditingEval(null);
        }}
      />
    </Box>
  );
}