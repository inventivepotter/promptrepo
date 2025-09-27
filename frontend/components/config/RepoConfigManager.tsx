'use client';

import React, { useEffect } from 'react';
import {
  Box,
  Button,
  VStack,
  HStack,
  Text,
  Spinner,
  Center,
  Combobox,
  createListCollection,
} from '@chakra-ui/react';
import { FaChevronDown } from 'react-icons/fa';
import { useColorModeValue } from '@/components/ui/color-mode';
import { 
  useConfig, 
  useAvailableRepos, 
  useConfigActions,
  useConfigError,
} from '@/stores/configStore';
import type { RepoInfo } from '@/stores/configStore';

interface BranchInfo {
  name: string;
  is_default: boolean;
}

interface RepoConfigManagerProps {
  disabled?: boolean;
}

export const RepoConfigManager = ({ disabled = false }: RepoConfigManagerProps) => {
  const config = useConfig();
  const availableRepos = useAvailableRepos();
  const error = useConfigError();
  const {
    addRepoConfig,
    removeRepoConfig,
    loadRepos,
    updateConfig,
    getConfig,
  } = useConfigActions();
  
  // Local state for form
  const [selectedRepo, setSelectedRepo] = React.useState<string>('');
  const [selectedBranch, setSelectedBranch] = React.useState<string>('');
  const [isLoadingRepos, setIsLoadingRepos] = React.useState(false);
  const [isSaving, setIsSaving] = React.useState(false);
  const [isLoadingBranches, setIsLoadingBranches] = React.useState(false);
  const [availableBranches, setAvailableBranches] = React.useState<BranchInfo[]>([]);

  // Search states for comboboxes
  const [repoSearchValue, setRepoSearchValue] = React.useState('');
  const [branchSearchValue, setBranchSearchValue] = React.useState('');

  // Theme values - called at top level
  const errorBg = useColorModeValue('red.50', 'red.900');

  // Load repos and config on mount
  useEffect(() => {
    const loadData = async () => {
      setIsLoadingRepos(true);
      try {
        await Promise.all([
          loadRepos(),
          getConfig()
        ]);
      } catch (error) {
        console.error('Failed to load data:', error);
      } finally {
        setIsLoadingRepos(false);
      }
    };
    loadData();
  }, [loadRepos, getConfig]);

  // Fetch branches when a repository is selected
  useEffect(() => {
    const fetchBranches = async () => {
      if (!selectedRepo) {
        setAvailableBranches([]);
        return;
      }

      setIsLoadingBranches(true);
      try {
        // Parse owner and repo from full_name (e.g., "owner/repo")
        const [owner, repo] = selectedRepo.split('/');
        
        const response = await fetch(`/api/v0/repos/branches?owner=${owner}&repo=${repo}`, {
          method: 'GET',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (response.ok) {
          const result = await response.json();
          if (result.status === 'success' && result.data) {
            setAvailableBranches(result.data.branches || []);
            // Set default branch as selected if no branch is selected
            if (!selectedBranch && result.data.default_branch) {
              setSelectedBranch(result.data.default_branch);
              setBranchSearchValue(result.data.default_branch);
            }
          }
        } else {
          console.error('Failed to fetch branches');
          // Fallback to default branch from repo info
          const repoInfo = availableRepos.find(r => r.full_name === selectedRepo);
          if (repoInfo) {
            setAvailableBranches([{
              name: repoInfo.default_branch,
              is_default: true
            }]);
            if (!selectedBranch) {
              setSelectedBranch(repoInfo.default_branch);
              setBranchSearchValue(repoInfo.default_branch);
            }
          }
        }
      } catch (error) {
        console.error('Error fetching branches:', error);
        // Fallback to default branch
        const repoInfo = availableRepos.find(r => r.full_name === selectedRepo);
        if (repoInfo) {
          setAvailableBranches([{
            name: repoInfo.default_branch,
            is_default: true
          }]);
          if (!selectedBranch) {
            setSelectedBranch(repoInfo.default_branch);
            setBranchSearchValue(repoInfo.default_branch);
          }
        }
      } finally {
        setIsLoadingBranches(false);
      }
    };

    fetchBranches();
  }, [selectedRepo, availableRepos]);

  const handleAddRepoConfig = async () => {
    if (!selectedRepo) return;

    const repoInfo = availableRepos.find(r => r.full_name === selectedRepo);
    if (!repoInfo) return;

    setIsSaving(true);
    try {
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
      setSelectedRepo('');
      setSelectedBranch('');
      setRepoSearchValue('');
      setBranchSearchValue('');
    } catch (error) {
      console.error('Failed to add repository:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleRemoveRepoConfig = async (index: number) => {
    setIsSaving(true);
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
    } finally {
      setIsSaving(false);
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
  
  // Filter branches based on search
  const filteredBranches = availableBranches.filter(branch =>
    branch.name.toLowerCase().includes(branchSearchValue.toLowerCase())
  );

  return (
    <Box p={6} borderWidth="1px" borderRadius="md" borderColor="border.emphasized">
      <VStack gap={6} align="stretch">
        <Text fontSize="lg" fontWeight="bold">Repository Configuration</Text>
        <Box fontSize="sm" opacity={0.7}>
          Configure repositories containing prompts to access them in the application.
        </Box>

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
        {isLoadingRepos ? (
          <Center py={8}>
            <VStack gap={3}>
              <Spinner size="lg" color="blue.500" />
              <Text opacity={0.7}>Loading repositories...</Text>
            </VStack>
          </Center>
        ) : (
          <VStack gap={4}>
            {/* Add Repository Section */}
            <Box p={6} borderWidth="1px" borderRadius="md" borderColor="border.muted" width="100%">
              <VStack gap={4}>
                <HStack gap={4} width="100%" align="end">
                  {/* Repository Combobox */}
                  <Box flex={1}>
                    <Text mb={2} fontWeight="medium">Repository</Text>
                    <Combobox.Root
                      collection={createListCollection({
                        items: filteredRepos.map(r => ({ label: r.name, value: r.full_name }))
                      })}
                      value={[selectedRepo]}
                      onValueChange={(e) => {
                        setSelectedRepo(e.value?.[0] || '');
                        if (selectedRepo !== e.value?.[0]) {
                          setSelectedBranch('');
                          setBranchSearchValue('');
                        }
                      }}
                      inputValue={repoSearchValue}
                      onInputValueChange={(e) => setRepoSearchValue(e.inputValue)}
                      openOnClick
                      disabled={isLoadingRepos || disabled || isSaving}
                    >
                      <Combobox.Control position="relative">
                        <Combobox.Input
                          placeholder={isLoadingRepos ? "Loading repositories..." : "Select or search repository"}
                          paddingRight="2rem"
                        />
                        <Combobox.Trigger position="absolute" right="0.5rem" top="50%" transform="translateY(-50%)">
                          <FaChevronDown size={16} />
                        </Combobox.Trigger>
                      </Combobox.Control>
                      <Combobox.Positioner>
                        <Combobox.Content>
                          {isLoadingRepos ? (
                            <Box p={2} textAlign="center" opacity={0.7}>
                              Loading repositories...
                            </Box>
                          ) : filteredRepos.length === 0 ? (
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
                  </Box>
                  
                  {/* Branch Combobox - only show when repo is selected */}
                  {selectedRepo && (
                    <Box flex={1}>
                      <Text mb={2} fontWeight="medium">Branch</Text>
                      <Combobox.Root
                        collection={createListCollection({
                          items: filteredBranches.map(b => ({
                            label: b.is_default ? `${b.name} (default)` : b.name,
                            value: b.name
                          }))
                        })}
                        value={[selectedBranch]}
                        onValueChange={(e) => setSelectedBranch(e.value?.[0] || '')}
                        inputValue={branchSearchValue}
                        onInputValueChange={(e) => setBranchSearchValue(e.inputValue)}
                        openOnClick
                        disabled={isSaving || isLoadingBranches}
                      >
                        <Combobox.Control position="relative">
                          <Combobox.Input
                            placeholder={isLoadingBranches ? "Loading branches..." : "Select or search branch"}
                            paddingRight="2rem"
                          />
                          <Combobox.Trigger position="absolute" right="0.5rem" top="50%" transform="translateY(-50%)">
                            <FaChevronDown size={16} />
                          </Combobox.Trigger>
                        </Combobox.Control>
                        <Combobox.Positioner>
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
                    </Box>
                  )}

                  <Button
                    onClick={handleAddRepoConfig}
                    disabled={!selectedRepo || !selectedBranch || disabled || isSaving}
                    alignSelf="end"
                  >
                    Add Repository
                  </Button>
                </HStack>
              </VStack>
            </Box>
            
            {/* Configured Repositories */}
            {(config.repo_configs && config.repo_configs.length > 0) && (
              <Box p={6} borderWidth="1px" borderRadius="md" borderColor="border.muted" width="100%">
                <Text fontWeight="bold" mb={4}>Selected Repositories</Text>
                <VStack gap={2}>
                  {config.repo_configs.map((repoConfig, index) => {
                    const repo = availableRepos.find(r => r.full_name === repoConfig.repo_name);
                    return (
                      <HStack key={index} justify="space-between" width="100%" p={2} bg="bg.subtle" borderRadius="md">
                        <Text fontSize="sm" fontWeight="400">
                          {repo?.name || repoConfig.repo_name} ({repoConfig.base_branch})
                        </Text>
                        <Button
                          size="sm"
                          onClick={() => handleRemoveRepoConfig(index)}
                          disabled={disabled || isLoadingRepos || isSaving}
                        >
                          Remove
                        </Button>
                      </HStack>
                    );
                  })}
                </VStack>
              </Box>
            )}
          </VStack>
        )}
      </VStack>
    </Box>
  );
};