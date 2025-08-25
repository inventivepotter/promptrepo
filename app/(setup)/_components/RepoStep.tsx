"use client"

import React from "react";
import { FaChevronDown } from 'react-icons/fa';
import {
  VStack,
  Box,
  Text,
  Button,
  Combobox,
  createListCollection,
  HStack,
} from '@chakra-ui/react'

interface Repo {
  id: number
  name: string
  fullName: string
  branches: string[]
}

interface SelectedRepo {
  repoId: number
  branch: string
}

interface RepoStepProps {
  isLoggedIn: boolean
  handleGitHubLogin: () => void
  selectedRepo: string
  setSelectedRepo: (id: string) => void
  selectedBranch: string
  setSelectedBranch: (branch: string) => void
  selectedRepos: SelectedRepo[]
  toggleRepoSelection: (repoId: number, branch: string) => void
}

export const SAMPLE_REPOS: Repo[] = [
  { id: 1, name: 'my-project', fullName: 'user/my-project', branches: ['main', 'develop', 'feature/auth'] },
  { id: 2, name: 'web-app', fullName: 'user/web-app', branches: ['main', 'staging'] },
  { id: 3, name: 'api-server', fullName: 'user/api-server', branches: ['main', 'v2', 'hotfix'] }
];

export default function RepoStep({
  isLoggedIn,
  handleGitHubLogin,
  selectedRepo,
  setSelectedRepo,
  selectedBranch,
  setSelectedBranch,
  selectedRepos,
  toggleRepoSelection
}: RepoStepProps) {
  const repos = SAMPLE_REPOS;
  // Force re-render after repo selection to fix conditional rendering
  const [repoChanged, setRepoChanged] = React.useState(false);

  React.useEffect(() => {
    setRepoChanged(false);
  }, [selectedRepo]);
  return (
    <Box p={6} borderWidth="1px" borderRadius="md" borderColor="border.emphasized">
      <VStack gap={6} align="stretch">
        <Text fontSize="lg" fontWeight="bold">Repository Selection</Text>
        <Text fontSize="sm" opacity={0.7} mb={2}>
          Select repositories and branches to clone.
        </Text>
        {!isLoggedIn ? (
          <Box p={6} textAlign="center" borderWidth="1px" borderRadius="md" borderColor="border.muted">
            <VStack gap={4}>
              <Text>Please login with GitHub to access your repositories</Text>
              <Button onClick={handleGitHubLogin}>
                Login with GitHub
              </Button>
            </VStack>
          </Box>
        ) : (
          <VStack gap={4}>
            <Box
              p={2}
              bg="green.subtle"
              borderRadius="sm"
              borderLeft="4px solid"
              borderColor="green.solid"
              position="fixed"
              top="20px"
              right="20px"
              zIndex={1000}
              boxShadow="md"
            >
              <Text fontWeight="normal" fontSize="sm" color="green.600" letterSpacing="0.01em">
                Successfully logged in to GitHub!
              </Text>
            </Box>
            {/* Repository Selection */}
            <Box p={6} borderWidth="1px" borderRadius="md" borderColor="border.muted" width="100%">
              <VStack gap={4}>
                <Box width="100%">
                  <Text mb={2} fontWeight="medium">Repository</Text>
                  <Combobox.Root
                    collection={createListCollection({
                      items: repos.map(r => ({ label: r.fullName, value: r.id.toString() }))
                    })}
                    value={[selectedRepo]}
                    onValueChange={(e) => {
                      // Debug: log event and value
                      console.log('Repo Combobox onValueChange', e);
                      setSelectedRepo(e.value?.[0] || '');
                      setRepoChanged(true);
                      if (selectedRepo !== e.value?.[0]) {
                        setSelectedBranch('');
                      }
                    }}
                    openOnClick
                  >
                    <Combobox.Control position="relative">
                      <Combobox.Input
                        placeholder="Select or search repository"
                        paddingRight="2rem"
                      />
                      <Combobox.Trigger position="absolute" right="0.5rem" top="50%" transform="translateY(-50%)">
                        <FaChevronDown size={16} />
                      </Combobox.Trigger>
                    </Combobox.Control>
                    <Combobox.Positioner>
                      <Combobox.Content>
                        {repos.map(repo => (
                          <Combobox.Item key={repo.id} item={repo.id.toString()}>
                            <Combobox.ItemText>{repo.fullName}</Combobox.ItemText>
                            <Combobox.ItemIndicator />
                          </Combobox.Item>
                        ))}
                      </Combobox.Content>
                    </Combobox.Positioner>
                  </Combobox.Root>
                </Box>
                {selectedRepo && (
                  <Box width="100%">
                    <Text mb={2} fontWeight="medium">Branch</Text>
                    <Combobox.Root
                      collection={createListCollection({
                        items: (repos.find(r => r.id.toString() === selectedRepo)?.branches || []).map(b => ({ label: b, value: b }))
                      })}
                      value={[selectedBranch]}
                      onValueChange={(e) => setSelectedBranch(e.value[0] || '')}
                      openOnClick
                    >
                      <Combobox.Control position="relative">
                        <Combobox.Input
                          placeholder="Select or search branch"
                          paddingRight="2rem"
                        />
                        <Combobox.Trigger position="absolute" right="0.5rem" top="50%" transform="translateY(-50%)">
                          <FaChevronDown size={16} />
                        </Combobox.Trigger>
                      </Combobox.Control>
                      <Combobox.Positioner>
                        <Combobox.Content>
                          {repos.find(r => r.id.toString() === selectedRepo)?.branches.map(branch => (
                            <Combobox.Item key={branch} item={branch}>
                              <Combobox.ItemText>{branch}</Combobox.ItemText>
                              <Combobox.ItemIndicator />
                            </Combobox.Item>
                          ))}
                        </Combobox.Content>
                      </Combobox.Positioner>
                    </Combobox.Root>
                  </Box>
                )}
                <Button
                  onClick={() => {
                    if (selectedRepo && selectedBranch) {
                      toggleRepoSelection(parseInt(selectedRepo), selectedBranch)
                      setSelectedRepo('')
                      setSelectedBranch('')
                    }
                  }}
                  disabled={!selectedRepo || !selectedBranch}
                >
                  Add Repository
                </Button>
              </VStack>
            </Box>
            {selectedRepos.length > 0 && (
              <Box p={6} borderWidth="1px" borderRadius="md" borderColor="border.muted" width="100%">
                <Text fontWeight="bold" mb={4}>Selected Repositories</Text>
                <VStack gap={2}>
                  {selectedRepos.map((selected, index) => {
                    const repo = repos.find(r => r.id === selected.repoId)
                    return (
                      <HStack key={index} justify="space-between" width="100%" p={2} bg="bg.subtle" borderRadius="md">
                        <Text fontSize="sm" fontWeight="400">
                          {repo?.fullName} ({selected.branch})
                        </Text>
                        <Button size="sm" onClick={() => toggleRepoSelection(selected.repoId, selected.branch)}>
                          Remove
                        </Button>
                      </HStack>
                    )
                  })}
                </VStack>
              </Box>
            )}
          </VStack>
        )}
      </VStack>
    </Box>
  )
}