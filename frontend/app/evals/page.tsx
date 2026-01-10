'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  VStack,
  Grid,
  Box,
  Container,
  ScrollArea,
  SkeletonText,
  EmptyState,
  Button,
  ButtonGroup,
} from '@chakra-ui/react';
import { FaFlask, FaGitAlt } from 'react-icons/fa';
import { useEvalStore } from '@/stores/evalStore';
import { useConfigStore } from '@/stores/configStore/configStore';
import { useSelectedRepository, useRepositoryFilterActions } from '@/stores/repositoryFilterStore';
import { EvalHeader } from '@/components/EvalHeader';
import { EvalCard } from '@/components/evals/EvalCard';
import { buildEvalEditorUrl } from '@/lib/urlEncoder';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';

function EvalsPageContent() {
  const router = useRouter();
  
  // Use eval store
  const evals = useEvalStore((state) => state.evals);
  const isLoading = useEvalStore((state) => state.isLoading);
  const fetchEvals = useEvalStore((state) => state.fetchEvals);
  const setSelectedRepo = useEvalStore((state) => state.setSelectedRepo);
  
  // Use shared repository filter store
  const selectedRepository = useSelectedRepository();
  const { setSelectedRepository } = useRepositoryFilterActions();
  
  // Use config store to check if repositories are configured
  const config = useConfigStore((state) => state.config);
  const hasConfiguredRepos = Boolean(config?.repo_configs?.length);

  // Initialize: clear selected repository if it's not in the configured repos
  useEffect(() => {
    if (typeof window !== 'undefined' && config?.repo_configs) {
      const configuredRepoNames = config.repo_configs.map(r => r.repo_name);
      
      // If selected repository is not in configured repos, clear it
      if (selectedRepository && !configuredRepoNames.includes(selectedRepository)) {
        setSelectedRepository('');
      }
    }
  }, [config, selectedRepository, setSelectedRepository]);

  // Fetch evals only when a valid repository is selected
  useEffect(() => {
    // Only fetch if we have a non-empty selectedRepository and it's in the configured repos
    if (typeof window !== 'undefined' &&
        selectedRepository &&
        selectedRepository.trim() !== '' &&
        config?.repo_configs?.some(r => r.repo_name === selectedRepository)) {
      fetchEvals(selectedRepository);
      setSelectedRepo(selectedRepository);
    }
  }, [selectedRepository, config, fetchEvals, setSelectedRepo]);

  const handleViewEval = (filePath: string) => {
    if (selectedRepository) {
      router.push(buildEvalEditorUrl(selectedRepository, filePath));
    }
  };

  const handleAddRepositories = () => {
    router.push('/config#repositories');
  };

  const handleCreateEval = () => {
    if (selectedRepository) {
      router.push(buildEvalEditorUrl(selectedRepository, 'new'));
    }
  };

  return (
    <Box height="100vh" width="100%" display="flex" flexDirection="column">
      {/* Evals Header - Outside ScrollArea */}
      <EvalHeader />

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
              <Container maxW="7xl" py={6}>
                <VStack gap={6} align="stretch">
                  {/* Evals grid */}
                  {isLoading ? (
                    <Grid
                      templateColumns={{
                        base: '1fr',
                        md: 'repeat(2, 1fr)',
                        lg: 'repeat(3, 1fr)',
                      }}
                      gap={6}
                    >
                      {[...Array(6)].map((_, index) => (
                        <Box
                          key={index}
                          p={6}
                          borderRadius="md"
                          bg="bg.subtle"
                          borderWidth="1px"
                          borderColor="transparent"
                          minHeight="200px"
                        >
                          <SkeletonText
                            noOfLines={3}
                            gap={5}
                            height={5}
                            opacity={0.2}
                          />
                        </Box>
                      ))}
                    </Grid>
                  ) : evals.length === 0 ? (
                    <EmptyState.Root>
                      <EmptyState.Content>
                        <EmptyState.Indicator>
                          {hasConfiguredRepos ? <FaFlask /> : <FaGitAlt />}
                        </EmptyState.Indicator>
                        <VStack textAlign="center">
                          <EmptyState.Title>
                            {hasConfiguredRepos ? 'Create your first eval' : 'Connect your first repository'}
                          </EmptyState.Title>
                          <EmptyState.Description>
                            {hasConfiguredRepos
                              ? 'You have repositories configured. Create your first eval to begin evaluating your prompts with DeepEval metrics.'
                              : 'Configure a repository first to discover and manage your AI prompts effectively.'
                            }
                          </EmptyState.Description>
                        </VStack>
                        <ButtonGroup>
                          {hasConfiguredRepos ? (
                            <Button onClick={handleCreateEval} disabled={!selectedRepository}>
                              Create Eval
                            </Button>
                          ) : (
                            <Button onClick={handleAddRepositories}>Add Repository</Button>
                          )}
                        </ButtonGroup>
                      </EmptyState.Content>
                    </EmptyState.Root>
                  ) : (
                    <Grid
                      templateColumns={{
                        base: '1fr',
                        md: 'repeat(2, 1fr)',
                        lg: 'repeat(3, 1fr)',
                      }}
                      gap={6}
                    >
                      {evals.map((evalData, index) => (
                        <EvalCard
                          key={`${selectedRepository}:${evalData.eval.name}:${index}`}
                          eval={evalData}
                          onView={handleViewEval}
                        />
                      ))}
                    </Grid>
                  )}
                </VStack>
              </Container>
            </Box>
          </ScrollArea.Content>
        </ScrollArea.Viewport>
        <ScrollArea.Scrollbar orientation="vertical">
          <ScrollArea.Thumb />
        </ScrollArea.Scrollbar>
      </ScrollArea.Root>
    </Box>
  );
}

export default function EvalsPage() {
  return (
    <ProtectedRoute>
      <EvalsPageContent />
    </ProtectedRoute>
  );
}