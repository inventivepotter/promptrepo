'use client';

import { useState, useEffect, useMemo } from 'react';
import { Combobox, createListCollection, Portal, Text, VStack } from '@chakra-ui/react';
import httpClient from '@/lib/httpClient';
import type { components } from '@/types/generated/api';
import { ResponseStatus, isStandardResponse } from '@/types/OpenApiResponse';

type PromptMeta = components['schemas']['PromptMeta'];

interface PromptSelectorProps {
  repoName: string;
  value: string;
  onChange: (promptPath: string, promptMeta?: PromptMeta) => void;
  disabled?: boolean;
}

export function PromptSelector({ repoName, value, onChange, disabled = false }: PromptSelectorProps) {
  const [availablePrompts, setAvailablePrompts] = useState<PromptMeta[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [inputValue, setInputValue] = useState('');

  // Load available prompts when repo changes
  useEffect(() => {
    const loadPrompts = async () => {
      if (!repoName) return;
      
      setIsLoading(true);
      try {
        const response = await httpClient.post<PromptMeta[]>(
          '/api/v0/prompts/discover',
          {
            repo_names: [repoName]
          }
        );
        
        if (response.status === ResponseStatus.SUCCESS && isStandardResponse(response) && response.data) {
          const prompts = Array.isArray(response.data) ? response.data : [];
          setAvailablePrompts(prompts);
        }
      } catch (error) {
        console.error('Failed to load prompts:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadPrompts();
  }, [repoName]);

  // Filter prompts based on input
  const filteredPrompts = useMemo(() => {
    if (!inputValue) return availablePrompts;
    
    const searchLower = inputValue.toLowerCase();
    return availablePrompts.filter(prompt => {
      const name = prompt.prompt?.name?.toLowerCase() || '';
      const description = prompt.prompt?.description?.toLowerCase() || '';
      const path = prompt.file_path?.toLowerCase() || '';
      
      return name.includes(searchLower) || 
             description.includes(searchLower) || 
             path.includes(searchLower);
    });
  }, [availablePrompts, inputValue]);

  // Create collection for prompt selection
  const promptCollection = useMemo(() => {
    return createListCollection({
      items: filteredPrompts.map(prompt => ({
        label: prompt.prompt?.name || 'Untitled',
        value: prompt.file_path,
        description: prompt.prompt?.description || ''
      })),
    });
  }, [filteredPrompts]);

  return (
    <Combobox.Root
      collection={promptCollection}
      value={value ? [value] : []}
      onValueChange={(e: { value: string[] }) => {
        if (e.value[0]) {
          const selectedPrompt = filteredPrompts.find(p => p.file_path === e.value[0]);
          onChange(e.value[0], selectedPrompt);
        }
      }}
      onInputValueChange={(e: { inputValue: string }) => {
        setInputValue(e.inputValue);
      }}
      inputValue={inputValue}
      openOnClick
      disabled={disabled || isLoading || availablePrompts.length === 0}
    >
      <Combobox.Control>
        <Combobox.Input 
          placeholder={
            isLoading 
              ? "Loading prompts..." 
              : availablePrompts.length === 0 
                ? "No prompts available" 
                : "Search or select a prompt"
          }
        />
        <Combobox.Trigger />
      </Combobox.Control>
      <Portal>
        <Combobox.Positioner style={{ zIndex: 99999 }}>
          <Combobox.Content style={{ zIndex: 99999 }}>
            {promptCollection.items.length === 0 ? (
              <Text p={2} fontSize="sm" color="fg.muted" textAlign="center">
                No prompts match your search
              </Text>
            ) : (
              promptCollection.items.map((prompt) => {
                const promptInfo = filteredPrompts.find(p => p.file_path === prompt.value);
                return (
                  <Combobox.Item key={prompt.value} item={prompt.value}>
                    <VStack align="start" gap={0}>
                      <Text fontSize="sm" fontWeight="medium">{prompt.label}</Text>
                      {promptInfo?.prompt?.description && (
                        <Text fontSize="xs" color="fg.muted">{promptInfo.prompt.description}</Text>
                      )}
                      <Text fontSize="xs" color="fg.muted" opacity={0.6} fontFamily="mono">
                        {prompt.value}
                      </Text>
                    </VStack>
                    <Combobox.ItemIndicator />
                  </Combobox.Item>
                );
              })
            )}
          </Combobox.Content>
        </Combobox.Positioner>
      </Portal>
    </Combobox.Root>
  );
}