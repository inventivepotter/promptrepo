'use client';

import { useEffect, useState } from 'react';
import {
  Box,
  Button,
  VStack,
  HStack,
  Text,
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
  useAvailableBranches,
  useIsLoadingBranches,
} from '@/stores/configStore';
import type { RepoInfo, BranchInfo } from '@/stores/configStore';

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
    updateConfig,
    fetchBranches,
    resetBranches,
  } = useConfigActions();
  
  // Local state for form
  const [selectedRepo, setSelectedRepo] = useState<string>('');
  const [selectedBranch, setSelectedBranch] = useState<string>('');
  const [isSaving, setIsSaving] = useState(false);
  const availableBranches = useAvailableBranches();
  const isLoadingBranches = useIsLoadingBranches();

  // Search states for comboboxes
  const [repoSearchValue, setRepoSearchValue] = useState('');
  const [branchSearchValue, setBranchSearchValue] = useState('');

  // Theme values - called at top level
  const errorBg = useColorModeValue('red.50', 'red.900');


  // Fetch branches when a repository is selected
  useEffect(() => {
    if (selectedRepo) {
      // Parse owner and repo from full_name (e.g., "owner/repo")
      const [owner, repo] = selectedRepo.split('/');
      fetchBranches(owner, repo);
      
      // Reset selected branch when repo changes
      setSelectedBranch('');
      setBranchSearchValue('');
    } else {
      resetBranches();
    }
  }, [selectedRepo]);

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
      resetBranches();
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
        {(
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
                      disabled={ disabled || isSaving}
                    >
                      <Combobox.Control position="relative">
                        <Combobox.Input
                          placeholder={"Select or search repository"}
                          paddingRight="2rem"
                        />
                        <Combobox.Trigger position="absolute" right="0.5rem" top="50%" transform="translateY(-50%)">
                          <FaChevronDown size={16} />
                        </Combobox.Trigger>
                      </Combobox.Control>
                      <Combobox.Positioner>
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
                          disabled={disabled || isSaving}
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