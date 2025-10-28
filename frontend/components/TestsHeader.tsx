'use client';

import React, { useMemo } from 'react';
import { useRouter } from 'next/navigation';
import {
  Box,
  Container,
  HStack,
  VStack,
  Text,
  Button,
  Select,
  Portal,
  createListCollection,
} from '@chakra-ui/react';
import { LuPlus } from 'react-icons/lu';
import { useSelectedRepository, useRepositoryFilterActions } from '@/stores/repositoryFilterStore';
import { useConfig } from '@/stores/configStore';
import { useTestStore } from '@/stores/testStore/testStore';
import { GetLatestButton } from './GetLatestButton';

export function TestsHeader() {
  const router = useRouter();
  const headerBg = "bg.subtle";
  
  // Use shared repository filter store
  const selectedRepository = useSelectedRepository();
  const { setSelectedRepository } = useRepositoryFilterActions();
  
  // Get available repositories from config
  const config = useConfig();
  const availableRepos = useMemo(() => {
    return config.repo_configs?.map(rc => rc.repo_name) || [];
  }, [config]);

  // Get fetchTestSuites to refresh after get latest
  const fetchTestSuites = useTestStore((state) => state.fetchTestSuites);

  const handleRefreshAfterGetLatest = async () => {
    if (selectedRepository) {
      await fetchTestSuites(selectedRepository);
    }
  };

  // Create collection for Select component
  const repoCollection = useMemo(
    () =>
      createListCollection({
        items: availableRepos.map((repo) => ({
          label: repo,
          value: repo,
        })),
      }),
    [availableRepos]
  );

  const handleCreateNew = () => {
    if (selectedRepository) {
      router.push(`/tests/new?repo_name=${encodeURIComponent(selectedRepository)}`);
    }
  };

  return (
    <Box
      bg={headerBg}
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
              Tests
            </Text>
            <Text fontSize="sm" color="text.secondary">
              Create and manage test suites for your prompts using DeepEval metrics
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
                        : "Select Repository"
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
              artifactType="test suites"
              onSuccess={handleRefreshAfterGetLatest}
              disabled={availableRepos.length === 0 || !selectedRepository}
            />
            <Button
              variant="solid"
              onClick={handleCreateNew}
              disabled={availableRepos.length === 0 || !selectedRepository}
            >
              <LuPlus /> New Test Suite
            </Button>
          </HStack>
        </HStack>
      </Container>
    </Box>
  );
}