'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  Dialog,
  Button,
  Input,
  Field,
  VStack,
  Combobox,
  createListCollection,
  Box,
} from '@chakra-ui/react';
import { FaChevronDown } from 'react-icons/fa';
import { useNewPromptForm } from '@/stores/promptStore';

interface CreatePromptModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function CreatePromptModal({ open, onOpenChange }: CreatePromptModalProps) {
  const router = useRouter();
  const { repositories, validateForm, createNewPrompt } = useNewPromptForm();

  const [selectedRepo, setSelectedRepo] = useState<string>('');
  const [filePath, setFilePath] = useState<string>('');
  const [isCreating, setIsCreating] = useState(false);
  const [errors, setErrors] = useState<{ repo?: string; filePath?: string }>({});
  const [repoSearchValue, setRepoSearchValue] = useState<string>('');
  
  // Filter repositories based on search
  const filteredRepos = repositories.filter((repo) =>
    repo.repo_name.toLowerCase().includes(repoSearchValue.toLowerCase())
  );

  const handleCreate = async () => {
    // Validate form using the hook
    const validationErrors = validateForm(selectedRepo, filePath);
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }

    setIsCreating(true);
    try {
      // Create the new prompt using the hook
      const newPrompt = await createNewPrompt(selectedRepo, filePath);

      if (newPrompt) {
        // Navigate to editor with the new prompt
        router.push(
          `/editor?repo_name=${encodeURIComponent(newPrompt.repo_name)}&file_path=${encodeURIComponent(newPrompt.file_path)}`
        );
        
        // Close modal and reset form
        onOpenChange(false);
        setSelectedRepo('');
        setFilePath('');
        setErrors({});
        setRepoSearchValue('');
      }
    } catch (error) {
      console.error('Failed to create prompt:', error);
      // Error notifications are already handled by promptsService
    } finally {
      setIsCreating(false);
    }
  };

  const handleCancel = () => {
    onOpenChange(false);
    // Reset form
    setSelectedRepo('');
    setFilePath('');
    setErrors({});
    setRepoSearchValue('');
  };

  return (
    <Dialog.Root open={open} onOpenChange={(e) => onOpenChange(e.open)}>
      <Dialog.Backdrop />
      <Dialog.Positioner>
        <Dialog.Content>
          <Dialog.Header>
            <Dialog.Title>Create New Prompt</Dialog.Title>
          </Dialog.Header>
          <Dialog.Body>
            <VStack gap={4} align="stretch">
              <Field.Root required invalid={!!errors.repo}>
                <Field.Label>Repository <Field.RequiredIndicator /></Field.Label>
                <Combobox.Root
                  collection={createListCollection({
                    items: filteredRepos.map((r) => ({ label: r.repo_name, value: r.repo_name })),
                  })}
                  value={selectedRepo ? [selectedRepo] : []}
                  onValueChange={(e) => {
                    setSelectedRepo(e.value?.[0] || '');
                    setErrors((prev) => ({ ...prev, repo: undefined }));
                  }}
                  inputValue={repoSearchValue}
                  onInputValueChange={(e) => setRepoSearchValue(e.inputValue)}
                  openOnClick
                  disabled={isCreating}
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
                  <Combobox.Positioner style={{ zIndex: 50 }}>
                    <Combobox.Content>
                      {filteredRepos.length === 0 ? (
                        <Box p={2} textAlign="center" opacity={0.7}>
                          {repositories.length === 0
                            ? 'No repositories configured'
                            : 'No matching repositories'}
                        </Box>
                      ) : (
                        filteredRepos.map((repo) => (
                          <Combobox.Item key={repo.repo_name} item={repo.repo_name}>
                            <Combobox.ItemText>{repo.repo_name}</Combobox.ItemText>
                            <Combobox.ItemIndicator />
                          </Combobox.Item>
                        ))
                      )}
                    </Combobox.Content>
                  </Combobox.Positioner>
                </Combobox.Root>
                {errors.repo && <Field.ErrorText>{errors.repo}</Field.ErrorText>}
              </Field.Root>

              <Field.Root required invalid={!!errors.filePath}>
                <Field.Label>File Path <Field.RequiredIndicator /></Field.Label>
                <Input
                  placeholder="_prompts/my-prompt.yaml"
                  value={filePath}
                  onChange={(e) => {
                    setFilePath(e.target.value);
                    setErrors((prev) => ({ ...prev, filePath: undefined }));
                  }}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      handleCreate();
                    }
                  }}
                  disabled={isCreating}
                />
                {errors.filePath && <Field.ErrorText>{errors.filePath}</Field.ErrorText>}
              </Field.Root>
            </VStack>
          </Dialog.Body>
          <Dialog.Footer>
            <Dialog.ActionTrigger asChild>
              <Button variant="outline" onClick={handleCancel} disabled={isCreating}>
                Cancel
              </Button>
            </Dialog.ActionTrigger>
            <Button
              onClick={handleCreate}
              loading={isCreating}
              disabled={isCreating}
            >
              Add
            </Button>
          </Dialog.Footer>
          <Dialog.CloseTrigger />
        </Dialog.Content>
      </Dialog.Positioner>
    </Dialog.Root>
  );
}