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
import { getAvailableRepos } from "../_lib/getAvailableRepos";
import { Repo } from "@/types/Repo";
import { useAuth } from "../../(auth)/_components/AuthProvider";

interface ReposProps {
  selectedRepo: string
  setSelectedRepo: (id: string) => void
  selectedBranch: string
  setSelectedBranch: (branch: string) => void
  configuredRepos: Repo[]
  toggleRepoSelection: (id: string, branch: string, name: string) => void
}

export default function Repos({
  selectedRepo,
  setSelectedRepo,
  selectedBranch,
  setSelectedBranch,
  configuredRepos,
  toggleRepoSelection
}: ReposProps) {
  const { user } = useAuth();
  const repos = getAvailableRepos();
  // Force re-render after repo selection to fix conditional rendering
  const [repoChanged, setRepoChanged] = React.useState(false);
  const [repoSearchValue, setRepoSearchValue] = React.useState('');
  const [branchSearchValue, setBranchSearchValue] = React.useState('');

  // Filter repositories based on search value
  const filteredRepos = repos.filter(repo =>
    repo.name.toLowerCase().includes(repoSearchValue.toLowerCase()) ||
    repo.id.toLowerCase().includes(repoSearchValue.toLowerCase())
  );

  // Filter branches based on search value
  const currentRepo = repos.find(r => r.id === selectedRepo);
  const filteredBranches = currentRepo?.all_branches?.filter(branch =>
    branch.toLowerCase().includes(branchSearchValue.toLowerCase())
  ) || [];

  React.useEffect(() => {
    setRepoChanged(false);
  }, [selectedRepo]);
  return (
    <Box p={6} borderWidth="1px" borderRadius="md" borderColor="border.emphasized">
      <VStack gap={6} align="stretch">
        <Text fontSize="lg" fontWeight="bold">Repository Selection</Text>
        <Text fontSize="sm" opacity={0.7} mb={2}>
          Select repositories and branches to associate with prompts.
        </Text>
        <VStack gap={4}>
            {user && (
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
                  Successfully logged in as {user.name}!
                </Text>
              </Box>
            )}
            {/* Repository Selection */}
            <Box p={6} borderWidth="1px" borderRadius="md" borderColor="border.muted" width="100%">
              <VStack gap={4}>
                <Box width="100%">
                  <Text mb={2} fontWeight="medium">Repository</Text>
                  <Combobox.Root
                    collection={createListCollection({
                      items: filteredRepos.map(r => ({ label: r.name, value: r.id }))
                    })}
                    value={[selectedRepo]}
                    onValueChange={(e) => {
                      setSelectedRepo(e.value?.[0] || '');
                      setRepoChanged(true);
                      if (selectedRepo !== e.value?.[0]) {
                        setSelectedBranch('');
                      }
                    }}
                    inputValue={repoSearchValue}
                    onInputValueChange={(e) => setRepoSearchValue(e.inputValue)}
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
                        {filteredRepos.map(repo => (
                          <Combobox.Item key={repo.id} item={repo.id}>
                            <Combobox.ItemText>{repo.name}</Combobox.ItemText>
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
                      const repo = repos.find(r => r.id === selectedRepo);
                      if (repo) {
                        toggleRepoSelection(repo.id, selectedBranch, repo.name)
                        setSelectedRepo('')
                        setSelectedBranch('')
                      }
                    }
                  }}
                  disabled={!selectedRepo || !selectedBranch}
                >
                  Add Repository
                </Button>
              </VStack>
            </Box>
            {configuredRepos.length > 0 && (
              <Box p={6} borderWidth="1px" borderRadius="md" borderColor="border.muted" width="100%">
                <Text fontWeight="bold" mb={4}>Selected Repositories</Text>
                <VStack gap={2}>
                  {configuredRepos.map((selected, index) => {
                    const repo = repos.find(r => r.id === selected.id)
                    return (
                      <HStack key={index} justify="space-between" width="100%" p={2} bg="bg.subtle" borderRadius="md">
                        <Text fontSize="sm" fontWeight="400">
                          {repo?.name} ({selected.base_branch})
                        </Text>
                        <Button size="sm" onClick={() => {
                          const repo = repos.find(r => r.id === selected.id);
                          if (repo) {
                            const name = repo.name;
                            toggleRepoSelection(selected.id, selected.base_branch || '', name);
                          }
                        }}>
                          Remove
                        </Button>
                      </HStack>
                    )
                  })}
                </VStack>
              </Box>
            )}
        </VStack>
      </VStack>
    </Box>
  )
}