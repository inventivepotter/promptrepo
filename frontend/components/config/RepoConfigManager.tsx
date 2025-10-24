'use client';

import {
  Box,
  Button,
  VStack,
  HStack,
  Text,
  Combobox,
  createListCollection,
  Field,
  Card,
  Fieldset,
  Stack,
  Skeleton,
  EmptyState,
  Collapsible,
} from '@chakra-ui/react';
import { useMemo, useState } from 'react';
import { FaChevronDown } from 'react-icons/fa';
import { LuGitBranch, LuChevronDown, LuChevronUp } from 'react-icons/lu';
import {
  useConfig,
  useAvailableRepos,
  useConfigActions,
  useConfigError,
  useAvailableBranches,
  useIsLoadingBranches,
  useRepoFormState,
  useIsLoadingConfig,
} from '@/stores/configStore';
import type { RepoInfo } from '@/stores/configStore';

interface RepoConfigManagerProps {
  disabled?: boolean;
}

export const RepoConfigManager = ({ disabled = false }: RepoConfigManagerProps) => {
  const [showRepoConfig, setShowRepoConfig] = useState(true);
  const config = useConfig();
  const availableRepos = useAvailableRepos();
  const error = useConfigError();
  const availableBranches = useAvailableBranches();
  const isLoadingBranches = useIsLoadingBranches();
  const isLoading = useIsLoadingConfig();
  
  const {
    addRepoConfig,
    removeRepoConfig,
    updateConfig,
    resetBranches,
    setSelectedRepoWithSideEffects,
    setSelectedBranch,
    setRepoSearchValue,
    setBranchSearchValue,
    resetRepoForm,
    setIsSaving,
  } = useConfigActions();
  
  // Repo form state from store
  const {
    selectedRepo,
    selectedBranch,
    isSaving,
    repoSearchValue,
    branchSearchValue,
  } = useRepoFormState();

  // Theme values - called at top level
  const borderColor = "border.elevated";
  const errorBg = { _light: 'red.50', _dark: 'red.900' };



  const handleAddRepoConfig = async () => {
    if (!selectedRepo) return;

    const repoInfo = availableRepos.find(r => r.full_name === selectedRepo);
    if (!repoInfo) return;

    try {
      setIsSaving(true);
      const repoConfig = {
        id: '', // Blank for new record
        repo_name: repoInfo.full_name, // Use full_name for consistency
        repo_url: repoInfo.clone_url,
        base_branch: selectedBranch || repoInfo.default_branch,
        current_branch: ''
      };

      // Add to local store
      addRepoConfig(repoConfig);

      // Update backend
      const updatedConfig = {
        ...config,
        repo_configs: [...(config.repo_configs || []), repoConfig]
      };
      await updateConfig(updatedConfig);

      // Reset selections
      resetRepoForm();
      resetBranches();
    } catch (error) {
      console.error('Failed to add repository:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleRemoveRepoConfig = async (index: number) => {
    try {
      // Remove from local store
      removeRepoConfig(index);

      // Update backend
      const updatedRepoConfigs = [...(config.repo_configs || [])];
      updatedRepoConfigs.splice(index, 1);
      const updatedConfig = {
        ...config,
        repo_configs: updatedRepoConfigs
      };
      await updateConfig(updatedConfig);
    } catch (error) {
      console.error('Failed to remove repository:', error);
    }
  };

  const getAvailableReposForSelection = (): RepoInfo[] => {
    const configuredRepos = config.repo_configs?.map(r => r.repo_name) || [];
    return availableRepos.filter(r => !configuredRepos.includes(r.full_name));
  };

  const availableForSelection = getAvailableReposForSelection();
  
  // Filter repositories based on search
  const filteredRepos = availableForSelection.filter(repo =>
    repo.name.toLowerCase().includes(repoSearchValue.toLowerCase()) ||
    repo.full_name.toLowerCase().includes(repoSearchValue.toLowerCase())
  );
  
  // Filter branches based on search - but if there's a selected branch, always include it
  const filteredBranches = useMemo(() => {
    if (!branchSearchValue) return availableBranches;
    
    return availableBranches.filter(branch =>
      branch.name.toLowerCase().includes(branchSearchValue.toLowerCase()) ||
      (branch.is_default && `${branch.name} (default)`.toLowerCase().includes(branchSearchValue.toLowerCase()))
    );
  }, [availableBranches, branchSearchValue]);

  return (
    <Card.Root
      id="repositories"
      borderWidth="1px"
      borderColor={borderColor}
      overflow="visible"
    >
      <Card.Body p={8} overflow="visible">
        <Fieldset.Root size="lg" overflow="visible">
          <HStack justify="space-between" align="center">
            <Stack flex={1}>
              <Fieldset.Legend>Repository Configuration</Fieldset.Legend>
              <Fieldset.HelperText>
                Configure repositories containing prompts to access them in the application.
              </Fieldset.HelperText>
            </Stack>
            <Button
              variant="ghost"
              _hover={{ bg: "bg.subtle" }}
              size="sm"
              onClick={() => setShowRepoConfig(!showRepoConfig)}
              aria-label={showRepoConfig ? "Collapse repository configuration" : "Expand repository configuration"}
            >
              <HStack gap={1}>
                <Text fontSize="xs" fontWeight="medium">
                  {showRepoConfig ? "Hide" : "Show"}
                </Text>
                {showRepoConfig ? <LuChevronUp /> : <LuChevronDown />}
              </HStack>
            </Button>
          </HStack>

          <Fieldset.Content overflow="visible">
            <Collapsible.Root open={showRepoConfig}>
              <Collapsible.Content overflow="visible">
                <VStack gap={6} align="stretch" mt={3}>
        {/* Error display */}
        {error && (
          <Box
            p={4}
            borderWidth="1px"
            borderRadius="md"
            borderColor="red.500"
            bg={errorBg}
          >
            <HStack gap={2}>
              <Text fontSize="sm" fontWeight="bold" color="red.500">
                Error:
              </Text>
              <Text fontSize="sm">{error}</Text>
            </HStack>
          </Box>
        )}

        {/* Loading state */}
        {(
          <VStack gap={4}>
            {/* Add Repository Section */}
            <Card.Root
              bg="transparent"
              borderWidth="1px"
              borderColor={borderColor}
              width="100%"
              overflow="visible"
            >
              <Card.Body p={8} overflow="visible">
                <VStack gap={4}>
                <HStack gap={4} width="100%" align="end">
                  {/* Repository Combobox */}
                  <Box flex={1}>
                    <Field.Root required>
                      <Field.Label>
                        Repository <Field.RequiredIndicator />
                      </Field.Label>
                      <Combobox.Root
                      collection={createListCollection({
                        items: filteredRepos.map(r => ({ label: r.name, value: r.full_name }))
                      })}
                      value={[selectedRepo]}
                      onValueChange={async (e) => {
                        await setSelectedRepoWithSideEffects(e.value?.[0] || '');
                      }}
                      inputValue={repoSearchValue}
                      onInputValueChange={(e) => setRepoSearchValue(e.inputValue)}
                      openOnClick
                      disabled={disabled || isSaving}
                      width="100%"
                    >
                      <Combobox.Control position="relative">
                        <Combobox.Input
                          placeholder={"Select or search repository"}
                          paddingRight="2rem"
                        />
                        <Combobox.Trigger position="absolute" right="0.5rem" top="50%" transform="translateY(-50%)">
                          <FaChevronDown size={10} />
                        </Combobox.Trigger>
                      </Combobox.Control>
                      <Combobox.Positioner style={{ zIndex: 50 }}>
                        <Combobox.Content>
                          {filteredRepos.length === 0 ? (
                            <Box p={2} textAlign="center" opacity={0.7}>
                              {availableForSelection.length === 0
                                ? 'All repositories configured or none available'
                                : 'No matching repositories'}
                            </Box>
                          ) : (
                            filteredRepos.map(repo => (
                              <Combobox.Item key={repo.full_name} item={repo.full_name}>
                                <Combobox.ItemText>{repo.name}</Combobox.ItemText>
                                <Combobox.ItemIndicator />
                              </Combobox.Item>
                            ))
                          )}
                        </Combobox.Content>
                      </Combobox.Positioner>
                        </Combobox.Root>
                      </Field.Root>
                    </Box>
                  
                  {/* Branch Combobox - always shown */}
                  <Box flex={1}>
                    <Field.Root required>
                      <Field.Label>
                        Branch <Field.RequiredIndicator />
                      </Field.Label>
                      <Combobox.Root
                      collection={createListCollection({
                        items: filteredBranches.map(b => ({
                          label: b.is_default ? `${b.name} (default)` : b.name,
                          value: b.name
                        }))
                      })}
                      value={selectedBranch ? [selectedBranch] : []}
                      onValueChange={(e) => {
                        const branch = e.value?.[0] || '';
                        setSelectedBranch(branch);
                      }}
                      inputValue={branchSearchValue}
                      onInputValueChange={(e) => {
                        const newValue = e.inputValue;
                        setBranchSearchValue(newValue);
                        
                        // Clear the selection if input doesn't match the selected branch
                        if (newValue === '' || (selectedBranch && !newValue.toLowerCase().includes(selectedBranch.toLowerCase()))) {
                          setSelectedBranch('');
                        }
                      }}
                      openOnClick
                      disabled={disabled || isSaving || isLoadingBranches || !selectedRepo}
                      width="100%"
                    >
                      <Combobox.Control position="relative">
                        <Combobox.Input
                          placeholder={!selectedRepo ? "Select a repository first" : (isLoadingBranches ? "Loading branches..." : "Select or search branch")}
                          paddingRight="2rem"
                          disabled={disabled || isSaving || isLoadingBranches || !selectedRepo}
                        />
                        <Combobox.Trigger position="absolute" right="0.5rem" top="50%" transform="translateY(-50%)">
                          <FaChevronDown size={10} />
                        </Combobox.Trigger>
                      </Combobox.Control>
                      <Combobox.Positioner style={{ zIndex: 50 }}>
                        <Combobox.Content>
                          {isLoadingBranches ? (
                            <Box p={2} textAlign="center" opacity={0.7}>
                              Loading branches...
                            </Box>
                          ) : filteredBranches.length === 0 ? (
                            <Box p={2} textAlign="center" opacity={0.7}>
                              {availableBranches.length === 0
                                ? 'No branches available'
                                : 'No matching branches'}
                            </Box>
                          ) : (
                            filteredBranches.map(branch => (
                              <Combobox.Item key={branch.name} item={branch.name}>
                                <Combobox.ItemText>
                                  {branch.is_default ? `${branch.name} (default)` : branch.name}
                                </Combobox.ItemText>
                                <Combobox.ItemIndicator />
                              </Combobox.Item>
                            ))
                          )}
                        </Combobox.Content>
                      </Combobox.Positioner>
                      </Combobox.Root>
                    </Field.Root>
                  </Box>

                  <Button
                    onClick={handleAddRepoConfig}
                    disabled={!selectedRepo || !selectedBranch || disabled || isSaving}
                    loading={isSaving}
                    loadingText="Saving..."
                    alignSelf="end"
                  >
                    Add Repository
                  </Button>
                </HStack>
              </VStack>
              </Card.Body>
            </Card.Root>
            
            {/* Configured Repositories */}
            {(config.repo_configs && config.repo_configs.length > 0) || isLoading ? (
              <Card.Root
                borderWidth="1px"
                borderColor={borderColor}
                width="100%"
                bg="transparent"
              >
                <Card.Body p={8}>
                  <Text fontWeight="semibold" fontSize="lg" mb={6}>Selected Repositories</Text>
                  {isLoading ? (
                    <VStack gap={4} width="100%">
                      {[1, 2].map((i) => (
                        <Skeleton key={i} height="60px" width="100%" bg="bg"/>
                      ))}
                    </VStack>
                  ) : (
                    <VStack gap={4}>
                    {config.repo_configs?.map((repoConfig, index) => {
                      const repo = availableRepos.find(r => r.full_name === repoConfig.repo_name);
                      return (
                        <Card.Root
                          key={index}
                          width="100%"
                          bg="bg.panel"
                          borderWidth="1px"
                          borderColor="border.subtle"
                          transition="all 0.2s"
                          _hover={{
                            borderColor: "border.emphasized",
                            shadow: "sm"
                          }}
                        >
                          <Card.Body p={5}>
                            <HStack justify="space-between" width="100%">
                              <HStack gap={3} flex={1} pr={2}>
                                <Box minWidth="90px">
                                  <Text fontSize="xs" color="fg.muted" mb={1}>Repository</Text>
                                  <Text fontSize="sm" fontWeight="semibold">{repo?.name || repoConfig.repo_name}</Text>
                                </Box>
                                <Box height="40px" width="1px" bg="border.subtle" />
                                <Box flex={1} px={2}>
                                  <Text fontSize="xs" color="fg.muted" mb={1}>Branch</Text>
                                  <Text fontSize="sm" fontWeight="semibold">{repoConfig.base_branch}</Text>
                                </Box>
                              </HStack>
                              <Button
                                size="sm"
                                variant="outline"
                                colorScheme="red"
                                onClick={() => handleRemoveRepoConfig(index)}
                                disabled={disabled || isSaving}
                              >
                                Remove
                              </Button>
                            </HStack>
                          </Card.Body>
                        </Card.Root>
                      );
                      })}
                    </VStack>
                  )}
                </Card.Body>
              </Card.Root>
            ) : (
              <Card.Root
                borderWidth="1px"
                borderColor={borderColor}
                width="100%"
                bg="transparent"
              >
                <Card.Body p={8}>
                  <EmptyState.Root>
                    <EmptyState.Content>
                      <EmptyState.Indicator>
                        <LuGitBranch />
                      </EmptyState.Indicator>
                      <VStack textAlign="center">
                        <EmptyState.Title>No repositories configured</EmptyState.Title>
                        <EmptyState.Description>
                          Add your first repository to get started
                        </EmptyState.Description>
                      </VStack>
                    </EmptyState.Content>
                  </EmptyState.Root>
                </Card.Body>
              </Card.Root>
            )}
          </VStack>
        )}
                </VStack>
              </Collapsible.Content>
            </Collapsible.Root>
          </Fieldset.Content>
        </Fieldset.Root>
      </Card.Body>
    </Card.Root>
  );
};
