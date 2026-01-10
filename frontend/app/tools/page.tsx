'use client';

import { useState, useEffect, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import {
  VStack,
  Text,
  Grid,
  Box,
  Container,
  ScrollArea,
  SkeletonText,
  EmptyState,
  Button,
  Input,
  HStack,
  Badge,
  Card,
  IconButton,
  createListCollection,
  Portal,
  Select,
  InputGroup,
  ButtonGroup,
} from '@chakra-ui/react';
import { HiPencil, HiTrash } from 'react-icons/hi';
import { LuSearch, LuWrench, LuPlus } from 'react-icons/lu';
import { FaGitAlt } from 'react-icons/fa';
import type { ToolMeta } from '@/types/tools';
import { ToolsService } from '@/services/tools';
import { successNotification } from '@/lib/notifications';
import { useConfig } from '@/stores/configStore';
import { useSelectedRepository, useRepositoryFilterActions } from '@/stores/repositoryFilterStore';
import { GetLatestButton } from '@/components/GetLatestButton';
import { buildToolEditorUrl } from '@/lib/urlEncoder';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { useIsAuthenticated, useIsInitialized } from '@/stores/authStore/hooks';

export default function ToolsPage() {
  const router = useRouter();
  const config = useConfig();
  const isAuthenticated = useIsAuthenticated();
  const isInitialized = useIsInitialized();
  const [tools, setTools] = useState<ToolMeta[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  
  // Use shared repository filter store
  const selectedRepository = useSelectedRepository();
  const { setSelectedRepository } = useRepositoryFilterActions();

  // Get available repositories from config
  const availableRepos = config.repo_configs || [];

  // Create collection for Select component
  const repoCollection = useMemo(
    () =>
      createListCollection({
        items: availableRepos.map((repo) => ({
          label: repo.repo_name,
          value: repo.repo_name,
        })),
      }),
    [availableRepos]
  );

  // Set initial repo when config loads
  useEffect(() => {
    if (availableRepos.length > 0 && !selectedRepository) {
      setSelectedRepository(availableRepos[0].repo_name);
    } else if (availableRepos.length === 0) {
      // No repos available, stop loading
      setIsLoading(false);
    }
  }, [availableRepos, selectedRepository, setSelectedRepository]);

  // Load tools when selected repo changes and user is authenticated
  useEffect(() => {
    if (selectedRepository && isAuthenticated && isInitialized) {
      loadTools();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedRepository, isAuthenticated, isInitialized]);

  const loadTools = async () => {
    if (!selectedRepository) return;
    
    try {
      setIsLoading(true);
      const data = await ToolsService.listTools(selectedRepository);
      setTools(data);
    } catch (error) {
      console.error('Failed to load tools:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRefreshAfterGetLatest = async () => {
    await loadTools();
  };

  const handleCreateNew = () => {
    if (selectedRepository) {
      router.push(buildToolEditorUrl(selectedRepository, 'new'));
    }
  };

  const handleEdit = (toolName: string) => {
    if (selectedRepository) {
      router.push(buildToolEditorUrl(selectedRepository, toolName));
    }
  };

  const handleDelete = async (toolName: string) => {
    if (!confirm(`Are you sure you want to delete "${toolName}"?`)) {
      return;
    }

    try {
      await ToolsService.deleteTool(toolName, selectedRepository);
      successNotification('Tool Deleted', `Successfully deleted "${toolName}"`);
      loadTools();
    } catch (error) {
      console.error('Failed to delete tool:', error);
    }
  };

  const handleAddRepositories = () => {
    router.push('/config#repositories');
  };

  // Filter tools based on search
  const filteredTools = tools.filter(tool =>
    (tool.tool?.tool?.name || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
    (tool.tool?.tool?.description || '').toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <ProtectedRoute>
      <Box height="100vh" width="100%" display="flex" flexDirection="column">
      {/* Header */}
      <Box
        bg="bg.subtle"
        borderBottom="1px solid"
        borderColor="bg.muted"
        py={4}
        position="sticky"
        top={0}
        zIndex={10}
      >
        <Container maxW="7xl" mx="auto">
          <HStack justify="space-between" align="center">
            <VStack align="start" gap={1}>
              <Text
                color="fg.muted"
                fontSize="2xl"
                letterSpacing="tight"
                fontWeight="1000"
              >
                Mock Tools
              </Text>
              <Text fontSize="sm" color="text.secondary">
                Create and manage mock tool definitions
              </Text>
            </VStack>
            
            <HStack gap={3} alignItems="flex-end">
              <Select.Root
                collection={repoCollection}
                size="sm"
                width="240px"
                value={selectedRepository ? [selectedRepository] : []}
                onValueChange={(e) => setSelectedRepository(e.value[0] || '')}
                disabled={availableRepos.length === 0}
              >
                <Select.Label fontSize="xs">Repository</Select.Label>
                <Select.HiddenSelect />
                <Select.Control>
                  <Select.Trigger>
                    <Select.ValueText
                      placeholder={
                        availableRepos.length === 0
                          ? "No repositories configured"
                          : "Select repository"
                      }
                    />
                  </Select.Trigger>
                  <Select.IndicatorGroup>
                    <Select.Indicator />
                  </Select.IndicatorGroup>
                </Select.Control>
                <Portal>
                  <Select.Positioner>
                    <Select.Content>
                      {repoCollection.items.map((repo) => (
                        <Select.Item item={repo} key={repo.value}>
                          {repo.label}
                          <Select.ItemIndicator />
                        </Select.Item>
                      ))}
                    </Select.Content>
                  </Select.Positioner>
                </Portal>
              </Select.Root>
              <GetLatestButton
                repoName={selectedRepository}
                onSuccess={handleRefreshAfterGetLatest}
                disabled={availableRepos.length === 0 || !selectedRepository}
              />
              <Button
                variant="solid"
                onClick={handleCreateNew}
                disabled={availableRepos.length === 0 || !selectedRepository}
              >
                <LuPlus /> New Tool
              </Button>
            </HStack>
          </HStack>
        </Container>
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
              <Container maxW="7xl" py={6}>
                <VStack gap={4} align="stretch">
                  {/* Search */}
                  {availableRepos.length > 0 && (
                    <Box maxW="md">
                      <InputGroup startElement={<LuSearch />}>
                        <Input
                          placeholder="Search tools..."
                          value={searchQuery}
                          onChange={(e) => setSearchQuery(e.target.value)}
                          variant="subtle"
                          size="sm"
                        />
                      </InputGroup>
                    </Box>
                  )}

                  {/* Tools grid */}
                  {availableRepos.length === 0 ? (
                    <EmptyState.Root>
                      <EmptyState.Content>
                        <EmptyState.Indicator>
                          <FaGitAlt />
                        </EmptyState.Indicator>
                        <VStack textAlign="center">
                          <EmptyState.Title>Connect your first repository</EmptyState.Title>
                          <EmptyState.Description>
                            Configure a repository first to discover and manage your AI prompts effectively.
                          </EmptyState.Description>
                        </VStack>
                        <ButtonGroup>
                          <Button onClick={handleAddRepositories}>Add Repository</Button>
                        </ButtonGroup>
                      </EmptyState.Content>
                    </EmptyState.Root>
                  ) : isLoading ? (
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
                  ) : filteredTools.length === 0 ? (
                    searchQuery ? (
                      <Box textAlign="center" py={12}>
                        <VStack gap={4}>
                          <Text fontSize="lg" color="gray.500">
                            No tools found matching your search.
                          </Text>
                        </VStack>
                      </Box>
                    ) : (
                      <EmptyState.Root>
                        <EmptyState.Content>
                          <EmptyState.Indicator>
                            <LuWrench />
                          </EmptyState.Indicator>
                          <VStack textAlign="center">
                            <EmptyState.Title>No tools yet</EmptyState.Title>
                            <EmptyState.Description>
                              Create your first mock tool to get started
                            </EmptyState.Description>
                          </VStack>
                          <Button onClick={handleCreateNew}>Create Tool</Button>
                        </EmptyState.Content>
                      </EmptyState.Root>
                    )
                  ) : (
                    <Grid
                      templateColumns={{
                        base: '1fr',
                        md: 'repeat(2, 1fr)',
                        lg: 'repeat(3, 1fr)',
                      }}
                      gap={6}
                    >
                      {filteredTools.map((toolMeta) => {
                        const tool = toolMeta.tool?.tool;
                        const toolName = tool?.name || '';
                        const toolDescription = tool?.description || '';
                        const mockEnabled = tool?.mock?.enabled || false;
                        const parameterCount = Object.keys(tool?.parameters?.properties || {}).length;
                        const requiredCount = tool?.parameters?.required?.length || 0;
                        
                        return (
                          <Card.Root
                            key={toolMeta.file_path}
                            borderWidth="1px"
                            borderColor="bg.muted"
                            _hover={{ bg: "bg.subtle" }}
                            transition="background-color 0.2s"
                          >
                            <Card.Body>
                              <VStack align="stretch" gap={3}>
                                <HStack justify="space-between">
                                  <Text fontSize="lg" fontWeight="bold">
                                    {toolName}
                                  </Text>
                                  <HStack gap={1}>
                                    <IconButton
                                      aria-label="Edit tool"
                                      size="sm"
                                      variant="ghost"
                                      onClick={() => handleEdit(toolMeta.file_path)}
                                    >
                                      <HiPencil />
                                    </IconButton>
                                    <IconButton
                                      aria-label="Delete tool"
                                      size="sm"
                                      variant="ghost"
                                      colorPalette="red"
                                      onClick={() => handleDelete(toolMeta.file_path)}
                                    >
                                      <HiTrash />
                                    </IconButton>
                                  </HStack>
                                </HStack>
                                
                                <Text fontSize="sm" color="gray.600" lineClamp={2}>
                                  {toolDescription}
                                </Text>

                                <HStack gap={2} flexWrap="wrap">
                                  <Badge colorPalette={mockEnabled ? 'green' : 'gray'}>
                                    {mockEnabled ? 'Mock Enabled' : 'Mock Disabled'}
                                  </Badge>
                                  <Badge colorPalette="blue">
                                    {parameterCount} param{parameterCount !== 1 ? 's' : ''}
                                  </Badge>
                                  {requiredCount > 0 && (
                                    <Badge colorPalette="orange">
                                      {requiredCount} required
                                    </Badge>
                                  )}
                                </HStack>
                              </VStack>
                            </Card.Body>
                          </Card.Root>
                        );
                      })}
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
    </ProtectedRoute>
  );
}