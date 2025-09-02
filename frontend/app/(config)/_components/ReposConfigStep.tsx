"use client"

import React from "react"
import { FaChevronDown } from 'react-icons/fa'
import { VStack, Box, Text, Button, Combobox, createListCollection, HStack, Input } from '@chakra-ui/react'
import { Repo } from "@/types/Repo"

interface ReposConfigStepProps {
  hostingType: string
  disabled?: boolean
  repos?: Repo[]
  configuredRepos?: Repo[]
  isLoadingRepos?: boolean
  isLoadingConfiguredRepos?: boolean
  updateConfiguredRepos?: (repos: Repo[]) => void
}

export default function ReposConfigStep({
  hostingType,
  disabled = false,
  repos = [],
  configuredRepos = [],
  isLoadingRepos = false,
  isLoadingConfiguredRepos = false,
  updateConfiguredRepos = () => {}
}: ReposConfigStepProps) {
  
  // Repository selection state
  const [selectedRepo, setSelectedRepo] = React.useState('')
  const [selectedBranch, setSelectedBranch] = React.useState('')
  const [selectedDirectory, setSelectedDirectory] = React.useState('')
  
  // Search states
  const [repoSearchValue, setRepoSearchValue] = React.useState('')
  const [branchSearchValue, setBranchSearchValue] = React.useState('')
  
  // Filter repositories and branches
  const filteredRepos = repos.filter(repo =>
    repo.name.toLowerCase().includes(repoSearchValue.toLowerCase()) ||
    repo.id.toLowerCase().includes(repoSearchValue.toLowerCase())
  )
  
  const currentRepo = repos.find(r => r.id === selectedRepo)
  const filteredBranches = currentRepo?.all_branches?.filter(branch =>
    branch.toLowerCase().includes(branchSearchValue.toLowerCase())
  ) || []

  const toggleRepoSelection = (id: string, branch: string, name: string, prompts_directory?: string) => {
    const existingIndex = configuredRepos.findIndex(r => r.id === id && r.base_branch === branch)
    
    if (existingIndex >= 0) {
      // Remove existing
      const updatedRepos = configuredRepos.filter((_, index) => index !== existingIndex)
      updateConfiguredRepos(updatedRepos)
    } else {
      // Add new
      const newRepo: Repo = {
        id,
        name,
        base_branch: branch,
        prompts_directory
      }
      const updatedRepos = [...configuredRepos, newRepo]
      updateConfiguredRepos(updatedRepos)
    }
  }

  const getInstructions = () => {
    switch (hostingType) {
      case 'individual':
        return {
          title: 'Personal Repository Setup',
          description: (
            <>
              Configure repositories containing prompts to access them in the application.
            </>
          )
        }
      
      case 'organization':
        return {
          title: 'Personal Repository Setup',
          description: (
            <>
              Configure your organization&apos;s prompt repositories to share prompts across your team.
            </>
          )
        }
      
      case 'multi-tenant':
        return {
          title: 'Multi-Tenant Repository Setup',
          description: (
            <>
              Configure repository access for multiple tenants. Each tenant can have their own set of prompt repositories.
            </>
          )
        }
      
      default:
        return {
          title: 'Repository Setup',
          description: (
            <>
              Configure repository access for prompt management.
            </>
          )
        }
    }
  }

  const { title, description } = getInstructions()

  return (
    <Box p={6} borderWidth="1px" borderRadius="md" borderColor="border.emphasized">
      <VStack gap={6} align="stretch">
        <Text fontSize="lg" fontWeight="bold">{title}</Text>
        <Box fontSize="sm" opacity={0.7}>
          {description}
        </Box>
        
        {/* Repository Selection Interface */}
        <VStack gap={4}>
          
          <Box p={6} borderWidth="1px" borderRadius="md" borderColor="border.muted" width="100%">
            <VStack gap={4}>
              <HStack gap={4} width="100%" align="end">
                <Box flex={1}>
                  <Text mb={2} fontWeight="medium">Repository</Text>
                  <Combobox.Root
                    collection={createListCollection({
                      items: filteredRepos.map(r => ({ label: r.name, value: r.id }))
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
                            <Combobox.Item key={repo.id} item={repo.id}>
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

                {selectedRepo && selectedBranch && (
                  <Box flex={1}>
                    <Text mb={2} fontWeight="medium">Directory</Text>
                    <Input
                      placeholder="Enter directory path (e.g., prompts)"
                      value={selectedDirectory}
                      onChange={(e) => setSelectedDirectory(e.target.value)}
                    />
                  </Box>
                )}

                <Button
                  onClick={() => {
                    if (selectedRepo && selectedBranch) {
                      const repo = repos.find(r => r.id === selectedRepo)
                      if (repo) {
                        toggleRepoSelection(repo.id, selectedBranch, repo.name, selectedDirectory || undefined)
                        setSelectedRepo('')
                        setSelectedBranch('')
                        setSelectedDirectory('')
                      }
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
                    const repo = repos.find(r => r.id === selected.id)
                    return (
                      <HStack key={index} justify="space-between" width="100%" p={2} bg="bg.subtle" borderRadius="md">
                        <Text fontSize="sm" fontWeight="400">
                          {repo?.name || selected.name} ({selected.base_branch}){selected.prompts_directory ? ` - ${selected.prompts_directory}` : ''}
                        </Text>
                        <Button
                          size="sm"
                          onClick={() => {
                            const repo = repos.find(r => r.id === selected.id)
                            if (repo) {
                              const name = repo.name
                              toggleRepoSelection(selected.id, selected.base_branch || '', name)
                            }
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
      </VStack>
    </Box>
  )
}