'use client';

import { useState } from 'react';
import { 
  Box, 
  VStack, 
  HStack, 
  Text, 
  Button, 
  IconButton,
  Badge
} from '@chakra-ui/react';
import { LuPlus, LuTrash2 } from 'react-icons/lu';
import { 
  useConfig, 
  useAvailableRepos, 
  useConfigActions
} from '@/stores/configStore';
import type { RepoInfo } from '@/stores/configStore';

interface RepoConfigManagerProps {
  disabled?: boolean;
}

export const RepoConfigManager = ({ disabled = false }: RepoConfigManagerProps) => {
  const config = useConfig();
  const availableRepos = useAvailableRepos();
  const { addRepoConfig, removeRepoConfig } = useConfigActions();
  
  const [selectedRepo, setSelectedRepo] = useState<string>('');

  const handleAddRepoConfig = () => {
    if (!selectedRepo) return;

    const repoInfo = availableRepos.find(r => r.full_name === selectedRepo);
    if (!repoInfo) return;

    const repoConfig = {
      id: '', // Blank for new record
      repo_name: repoInfo.name,
      repo_url: repoInfo.clone_url,
      base_branch: repoInfo.default_branch,
      current_branch: ''
    };

    addRepoConfig(repoConfig);
    setSelectedRepo('');
  };

  const handleRemoveRepoConfig = (repoId: string) => {
    removeRepoConfig(repoId);
  };

  const getAvailableReposForSelection = (): RepoInfo[] => {
    const configuredRepos = config.repo_configs?.map(r => r.repo_name) || [];
    return availableRepos.filter(r => !configuredRepos.includes(r.name));
  };

  return (
    <Box p={6} borderWidth="1px" borderRadius="md" borderColor="border.emphasized">
      <VStack gap={6} align="stretch">
        <Text fontSize="xl" fontWeight="bold">Repository Configuration</Text>
        <Text fontSize="sm" opacity={0.7}>
          Select repositories to include in your prompt library
        </Text>

        {/* Existing Configurations */}
        {config.repo_configs && config.repo_configs.length > 0 && (
          <VStack gap={3} align="stretch">
            <Text fontSize="md" fontWeight="semibold">Configured Repositories</Text>
            {config.repo_configs.map((repoConfig, index) => (
              <HStack 
                key={repoConfig.id || index}
                p={3}
                bg="gray.50"
                borderRadius="md"
                justify="space-between"
              >
                <VStack align="flex-start" gap={1}>
                  <HStack>
                    <Text fontWeight="medium">
                      {repoConfig.repo_name}
                    </Text>
                    <Badge colorScheme="green">
                      Enabled
                    </Badge>
                  </HStack>
                  <Text fontSize="sm" opacity={0.7}>
                    Branch: {repoConfig.base_branch}
                  </Text>
                  <Text fontSize="sm" opacity={0.7}>
                    Current: {repoConfig.current_branch || 'Not set'}
                  </Text>
                </VStack>
                <IconButton
                  aria-label={`Remove ${repoConfig.repo_name}`}
                  onClick={() => handleRemoveRepoConfig(repoConfig.id || index.toString())}
                  disabled={disabled}
                  size="sm"
                  variant="ghost"
                  colorScheme="red"
                >
                  <LuTrash2 />
                </IconButton>
              </HStack>
            ))}
          </VStack>
        )}

        {/* Add New Configuration */}
        <VStack gap={4} align="stretch">
          <Text fontSize="md" fontWeight="semibold">Add Repository</Text>
          
          {getAvailableReposForSelection().length === 0 ? (
            <Text fontSize="sm" color="gray.500">
              {availableRepos.length === 0 
                ? 'No repositories available. Please check your authentication.'
                : 'All available repositories have been configured'
              }
            </Text>
          ) : (
            <>
              <select
                value={selectedRepo}
                onChange={(e) => setSelectedRepo(e.target.value)}
                disabled={disabled}
                style={{
                  padding: '8px 12px',
                  borderRadius: '6px',
                  border: '1px solid #e2e8f0',
                  backgroundColor: 'white'
                }}
              >
                <option value="">Select a repository</option>
                {getAvailableReposForSelection().map((repo) => (
                  <option key={repo.full_name} value={repo.full_name}>
                    {repo.full_name} ({repo.private ? 'Private' : 'Public'})
                  </option>
                ))}
              </select>

              <Button
                onClick={handleAddRepoConfig}
                disabled={disabled || !selectedRepo}
                colorScheme="blue"
              >
                <LuPlus style={{ marginRight: '8px' }} />
                Add Repository
              </Button>
            </>
          )}
        </VStack>
      </VStack>
    </Box>
  );
};