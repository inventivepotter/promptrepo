"use client"

import React from "react"
import { FaChevronDown } from 'react-icons/fa'
import { VStack, Box, Text, Button, Combobox, createListCollection, HStack, List } from '@chakra-ui/react'
import type { components } from '@/types/generated/api';

type RepoInfo = components['schemas']['RepoInfo'];
type RepoConfig = components['schemas']['RepoConfig'];

interface ReposConfigStepProps {
  hostingType: string
  disabled?: boolean
  repos?: RepoInfo[]
  configuredRepos?: RepoConfig[]
  isLoadingRepos?: boolean
  isLoadingConfiguredRepos?: boolean
  addRepoConfig: (repoName: string, branch: string) => void
  removeRepoConfig: (index: number) => void
}

export default function ReposConfigStep({
  hostingType,
  disabled = false,
  repos = [],
  configuredRepos = [],
  isLoadingRepos = false,
  isLoadingConfiguredRepos = false,
  addRepoConfig,
  removeRepoConfig
}: ReposConfigStepProps) {
  
  // Repository selection state
  const [selectedRepo, setSelectedRepo] = React.useState('')
  const [selectedBranch, setSelectedBranch] = React.useState('')
  
  // Search states
  const [repoSearchValue, setRepoSearchValue] = React.useState('')
  const [branchSearchValue, setBranchSearchValue] = React.useState('')
  
  // Filter repositories and branches
  const filteredRepos = repos.filter(repo =>
    repo.name.toLowerCase().includes(repoSearchValue.toLowerCase()) ||
    repo.full_name.toLowerCase().includes(repoSearchValue.toLowerCase())
  )
  
  const currentRepo = repos.find(r => r.full_name === selectedRepo)
  // For now, we'll use a simple branch list - this should be extended when the API supports branch listing
  const filteredBranches = [currentRepo?.default_branch || 'main'].filter(branch =>
    branch.toLowerCase().includes(branchSearchValue.toLowerCase())
  )

  const handleAddRepo = (full_name: string, branch: string) => {
    addRepoConfig(full_name, branch);
    // Reset the selection after adding
    setSelectedRepo('');
    setSelectedBranch('');
  }

  const handleRemoveRepo = (index: number) => {
    removeRepoConfig(index);
  }


  return (
    <Box p={6} borderWidth="1px" borderRadius="md" borderColor="border.emphasized">
      <VStack gap={6} align="stretch">
        <Text fontSize="lg" fontWeight="bold">Repository Setup</Text>
        <Box fontSize="sm" opacity={0.7}>
          Configure repositories containing prompts to access them in the application.
        </Box>
        
        {/* Individual hosting type message */}
        {hostingType === 'individual' && (
          <Box
            p={5}
            borderWidth="1px"
            borderRadius="md"
            borderColor="border.muted"
            bg="bg.subtle"
          >
            <Text fontSize="md" fontWeight="semibold" mb={3} color="fg.emphasized">
              Individual Hosting Mode
            </Text>
            <VStack align="start" gap={3}>
              <Text fontSize="sm" opacity={0.9}>
                In individual hosting mode, prompts are loaded from local repositories. To get started:
              </Text>
              <List.Root as="ol" listStyle="decimal" fontSize="sm" opacity={0.9} pl={4}>
                <List.Item _marker={{ color: "inherit" }} mb={2}>
                  Create a <Text as="code" bg="bg.muted" px={1} borderRadius="sm" fontFamily="mono">repos</Text> folder in your promptrepo directory if it doesn&apos;t exist
                </List.Item>
                <List.Item _marker={{ color: "inherit" }} mb={2}>
                  Clone your prompt repositories into the <Text as="code" bg="bg.muted" px={1} borderRadius="sm" fontFamily="mono">repos</Text> folder
                </List.Item>
                <List.Item _marker={{ color: "inherit" }} mb={2}>
                  Example: <Text as="code" bg="bg.muted" px={1} borderRadius="sm" fontFamily="mono" fontSize="xs">git clone https://github.com/your-username/your-prompts.git repos/your-prompts</Text>
                </List.Item>
                <List.Item _marker={{ color: "inherit" }}>
                  The application will automatically discover and load prompts from all repositories in the repos folder
                </List.Item>
              </List.Root>
              <Text fontSize="xs" opacity={0.7}>
                Tip: You can have multiple repositories in the repos folder, and the application will load prompts from all of them.
              </Text>
            </VStack>
          </Box>
        )}
        
        {/* Repository Selection Interface - only show for non-individual hosting */}
        {hostingType !== 'individual' && (
        <VStack gap={4}>
          
          <Box p={6} borderWidth="1px" borderRadius="md" borderColor="border.muted" width="100%">
            <VStack gap={4}>
              <HStack gap={4} width="100%" align="end">
                <Box flex={1}>
                  <Text mb={2} fontWeight="medium">Repository</Text>
                  <Combobox.Root
                    collection={createListCollection({
                      items: filteredRepos.map(r => ({ label: r.name, value: r.full_name }))
                    })}
                    value={[selectedRepo]}
                    onValueChange={(e) => {
                      setSelectedRepo(e.value?.[0] || '')
                      if (selectedRepo !== e.value?.[0]) {
                        setSelectedBranch('')
                      }
                    }}
                    inputValue={repoSearchValue}
                    onInputValueChange={(e) => setRepoSearchValue(e.inputValue)}
                    openOnClick
                    disabled={isLoadingRepos || disabled}
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
                            No repositories available
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
                
                {selectedRepo && (
                  <Box flex={1}>
                    <Text mb={2} fontWeight="medium">Branch</Text>
                    <Combobox.Root
                      collection={createListCollection({
                        items: filteredBranches.map(b => ({ label: b, value: b }))
                      })}
                      value={[selectedBranch]}
                      onValueChange={(e) => setSelectedBranch(e.value[0] || '')}
                      inputValue={branchSearchValue}
                      onInputValueChange={(e) => setBranchSearchValue(e.inputValue)}
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
                          {filteredBranches.map(branch => (
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
                      handleAddRepo(selectedRepo, selectedBranch)
                    }
                  }}
                  disabled={!selectedRepo || !selectedBranch || disabled}
                  alignSelf="end"
                >
                  Add Repository
                </Button>
              </HStack>
            </VStack>
          </Box>
          
          {(isLoadingConfiguredRepos || configuredRepos.length > 0) && (
            <Box p={6} borderWidth="1px" borderRadius="md" borderColor="border.muted" width="100%">
              <Text fontWeight="bold" mb={4}>Selected Repositories</Text>
              {isLoadingConfiguredRepos ? (
                <Box textAlign="center" opacity={0.7}>
                  Loading configured repositories...
                </Box>
              ) : configuredRepos.length === 0 ? (
                <Box textAlign="center" opacity={0.7}>
                  No repositories configured
                </Box>
              ) : (
                <VStack gap={2}>
                  {configuredRepos.map((selected, index) => {
                    const repo = repos.find(r => r.full_name === selected.repo_name)
                    return (
                      <HStack key={index} justify="space-between" width="100%" p={2} bg="bg.subtle" borderRadius="md">
                        <Text fontSize="sm" fontWeight="400">
                          {repo?.name || selected.repo_name} ({selected.base_branch})
                        </Text>
                        <Button
                          size="sm"
                          onClick={() => {
                            handleRemoveRepo(index)
                          }}
                          disabled={disabled || isLoadingConfiguredRepos}
                        >
                          Remove
                        </Button>
                      </HStack>
                    )
                  })}
                </VStack>
              )}
            </Box>
          )}
        </VStack>
        )}
      </VStack>
    </Box>
  )
}