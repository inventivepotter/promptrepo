'use client';

import React from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Input,
  Textarea,
  NumberInput,
  Button,
  Combobox,
  createListCollection,
  Switch,
} from '@chakra-ui/react';
import { Tooltip } from '@/components/ui/tooltip';
import { FaChevronDown } from 'react-icons/fa';
import { LuArrowLeft, LuInfo } from 'react-icons/lu';
import { useColorModeValue } from '@/components/ui/color-mode';
import { Prompt } from '../_state/promptState';
import { getModelOptions } from '../_lib/getConfiguredModels';
import { SelectedRepo } from './Repos';

interface PromptEditorProps {
  prompt: Prompt | null;
  onSave: (updates: Partial<Prompt>) => void;
  onBack: () => void;
  selectedRepos?: Array<SelectedRepo>;
}

export function PromptEditor({ prompt, onSave, onBack, selectedRepos = [] }: PromptEditorProps) {
  const [formData, setFormData] = React.useState<Partial<Prompt>>({
    name: '',
    description: '',
    prompt: '',
    model: '',
    failover_model: '',
    temperature: 0.7,
    top_p: 1.0,
    max_tokens: 2048,
    thinking_enabled: false,
    thinking_budget: 20000,
  });
  
  const [showRepoError, setShowRepoError] = React.useState(false);
  const [isRepoSelected, setIsRepoSelected] = React.useState(!!formData.repo);

  // Theme colors
  const mutedTextColor = useColorModeValue('gray.600', 'gray.400');

  const modelOptions = getModelOptions();
  const modelCollection = createListCollection({
    items: modelOptions
  });

  // Update form data when prompt changes
  React.useEffect(() => {
    if (prompt) {
      // Only update formData if prompt has changed
      const isSame =
        formData.name === prompt.name &&
        formData.description === prompt.description &&
        formData.prompt === prompt.prompt &&
        formData.model === prompt.model &&
        formData.failover_model === prompt.failover_model &&
        formData.temperature === prompt.temperature &&
        formData.top_p === prompt.top_p &&
        formData.max_tokens === prompt.max_tokens &&
        formData.thinking_enabled === prompt.thinking_enabled &&
        formData.thinking_budget === prompt.thinking_budget;

      if (!isSame) {
        setFormData({
          name: prompt.name,
          description: prompt.description,
          prompt: prompt.prompt,
          model: prompt.model,
          failover_model: prompt.failover_model,
          temperature: prompt.temperature,
          top_p: prompt.top_p,
          max_tokens: prompt.max_tokens,
          thinking_enabled: prompt.thinking_enabled,
          thinking_budget: prompt.thinking_budget,
        });
      }
    } else {
      // Initialize with default values for new prompts
      setFormData({
        name: '',
        description: '',
        prompt: '',
        model: '',
        failover_model: '',
        temperature: 0.7,
        top_p: 1.0,
        max_tokens: 2048,
        thinking_enabled: false,
        thinking_budget: 20000,
      });
    }
  }, [prompt]);

  // Initialize formData with prompt data when component mounts
  React.useEffect(() => {
    if (prompt) {
      setFormData({
        name: prompt.name,
        description: prompt.description,
        prompt: prompt.prompt,
        model: prompt.model,
        failover_model: prompt.failover_model,
        temperature: prompt.temperature,
        top_p: prompt.top_p,
        max_tokens: prompt.max_tokens,
        thinking_enabled: prompt.thinking_enabled,
        thinking_budget: prompt.thinking_budget,
        repo: prompt.repo,
      });
    }
  }, [prompt]);

  const updateField = (field: keyof Prompt, value: string | number | boolean) => {
    // Check if repository is selected before allowing other field edits
    if (!formData.repo && !showRepoError) {
      setShowRepoError(true);
      return;
    }
    
    const updatedData = { ...formData, [field]: value };
    setFormData(updatedData);
    // Auto-save when data changes
    onSave(updatedData);
  };

  const updateRepoField = (repo: SelectedRepo | undefined) => {
    const updatedData = { ...formData, repo };
    setFormData(updatedData);
    setIsRepoSelected(!!repo); // Update selection state
    setShowRepoError(false); // Clear error when repository is selected
    // Auto-save when data changes
    onSave(updatedData);
  };

  const handleTemperatureChange = (value: string) => {
    const num = parseFloat(value);
    if (!isNaN(num) && num >= 0 && num <= 2) {
      updateField('temperature', Math.round(num * 100) / 100);
    }
  };

  const handleTopPChange = (value: string) => {
    const num = parseFloat(value);
    if (!isNaN(num) && num >= 0 && num <= 1) {
      updateField('top_p', Math.round(num * 100) / 100);
    }
  };

  // Create a default prompt if none is provided (for new prompts)
  const displayPrompt = prompt || {
    id: 'new',
    name: '',
    description: '',
    prompt: '',
    model: '',
    failover_model: '',
    temperature: 0.7,
    top_p: 1.0,
    max_tokens: 2048,
    thinking_enabled: false,
    thinking_budget: 20000,
    created_at: new Date(),
    updated_at: new Date(),
  };

  return (
    <Box p={6} borderWidth="1px" borderRadius="md" borderColor="border.emphasized">
      <VStack gap={6} align="stretch">
        {/* Header */}
        <HStack justify="space-between" align="center">
          <HStack gap={4}>
            <Button
              variant="ghost"
              onClick={onBack}
              size="sm"
            >
              <HStack gap={2}>
                <LuArrowLeft size={16} />
                <Text>Back</Text>
              </HStack>
            </Button>
            <VStack align="start" gap={1}>
              <Text fontSize="2xl" fontWeight="bold">
                {displayPrompt.name || 'New Prompt'}
              </Text>
              {displayPrompt.repo?.name && (
                <Text fontSize="sm" color={mutedTextColor}>
                  Repository: {displayPrompt.repo.name}
                </Text>
              )}
              <Text fontSize="sm" color={mutedTextColor}>
                Edit prompt settings and configuration. Changes are saved automatically.
              </Text>
            </VStack>
          </HStack>
        </HStack>

        {/* Form */}
        <Box p={6} borderWidth="1px" borderRadius="md" borderColor="border.muted">
          <VStack gap={6} align="stretch">
              {/* Basic Info */}
              <Box>
                <Text fontSize="lg" fontWeight="semibold" mb={4}>
                  Basic Information
                </Text>
                <VStack gap={4} align="stretch">

                  <Box>
                    <Text mb={2} fontWeight="semibold" color={!formData.repo ? "red.500" : undefined}>
                      Repository *
                    </Text>
                    {showRepoError && !formData.repo && (
                      <Text fontSize="sm" color="red.500" mb={2}>
                        Please select a repository before editing other fields
                      </Text>
                    )}
                    <Combobox.Root
                      collection={createListCollection({
                        items: selectedRepos.map(repo => ({
                          label: `${repo.name} (${repo.branch})`,
                          value: repo.id.toString()
                        }))
                      })}
                      value={formData.repo?.id ? [formData.repo.id.toString()] : []}
                      onValueChange={(e) => {
                        const id = parseInt(e.value[0] || '0');
                        const selectedRepo = selectedRepos.find(r => r.id === id);
                        if (selectedRepo) {
                          updateRepoField({
                            id: selectedRepo.id,
                            branch: selectedRepo.branch,
                            name: selectedRepo.name
                          });
                        } else {
                          updateRepoField(undefined);
                        }
                      }}
                      openOnClick
                    >
                      <Combobox.Control position="relative">
                        <Combobox.Input
                          placeholder={selectedRepos.length > 0 ? "Select repository" : "No repositories configured"}
                          paddingRight="2rem"
                        />
                        <Combobox.Trigger position="absolute" right="0.5rem" top="50%" transform="translateY(-50%)">
                          <FaChevronDown size={16} />
                        </Combobox.Trigger>
                      </Combobox.Control>
                      <Combobox.Positioner>
                        <Combobox.Content>
                          {selectedRepos.map(repo => (
                            <Combobox.Item key={repo.id} item={repo.id.toString()}>
                              <Combobox.ItemText>{repo.name} ({repo.branch})</Combobox.ItemText>
                              <Combobox.ItemIndicator />
                            </Combobox.Item>
                          ))}
                        </Combobox.Content>
                      </Combobox.Positioner>
                    </Combobox.Root>
                  </Box>

                  <Box opacity={!formData.repo ? 0.5 : 1}>
                    <Text mb={2} fontWeight={formData.repo ? "medium" : "normal"} color={!formData.repo ? "gray.400" : undefined}>Name</Text>
                    <Input
                      value={formData.name || ''}
                      onChange={(e) => updateField('name', e.target.value)}
                      placeholder="Enter prompt name"
                    />
                  </Box>

                  <Box opacity={!formData.repo ? 0.5 : 1}>
                    <Text mb={2} fontWeight={formData.repo ? "medium" : "normal"} color={!formData.repo ? "gray.400" : undefined} fontSize="lg">Prompt Template</Text>
                    <Text mb={3} fontSize="sm" color={mutedTextColor}>
                      This is the core of your prompt. Write your instructions, context, and any variables here.
                    </Text>
                    <Textarea
                      value={formData.prompt || ''}
                      onChange={(e) => updateField('prompt', e.target.value)}
                      placeholder="Enter your prompt template here..."
                      rows={15}
                      minH="400px"
                      lineHeight="1.6"
                      resize="vertical"
                    />
                  </Box>
                </VStack>
              </Box>

              {/* Model Configuration */}
              <Box opacity={!formData.repo ? 0.5 : 1}>
                <Text fontSize="lg" fontWeight="semibold" mb={4}>
                  Model Configuration
                </Text>
                <VStack gap={4} align="stretch">
                  <HStack gap={4}>
                    <Box flex={1}>
                      <HStack mb={2}>
                        <Text fontWeight={formData.repo ? "medium" : "normal"} color={!formData.repo ? "gray.400" : undefined}>Primary Model</Text>
                        <Tooltip content="Select the main model used for generating responses.">
                          <Box cursor="help">
                            <LuInfo size={14} opacity={0.6} />
                          </Box>
                        </Tooltip>
                      </HStack>
                      <Combobox.Root
                        collection={modelCollection}
                        value={[formData.model || '']}
                        onValueChange={(e) => updateField('model', e.value[0] || '')}
                        openOnClick
                      >
                        <Combobox.Control position="relative">
                          <Combobox.Input
                            placeholder="Select primary model"
                            paddingRight="2rem"
                          />
                          <Combobox.Trigger position="absolute" right="0.5rem" top="50%" transform="translateY(-50%)">
                            <FaChevronDown size={16} />
                          </Combobox.Trigger>
                        </Combobox.Control>
                        <Combobox.Positioner>
                          <Combobox.Content>
                            {modelOptions.map(option => (
                              <Combobox.Item key={option.value} item={option.value}>
                                <Combobox.ItemText>{option.label}</Combobox.ItemText>
                                <Combobox.ItemIndicator />
                              </Combobox.Item>
                            ))}
                          </Combobox.Content>
                        </Combobox.Positioner>
                      </Combobox.Root>
                    </Box>

                    <Box flex={1}>
                      <HStack mb={2}>
                        <Text fontWeight={formData.repo ? "medium" : "normal"} color={!formData.repo ? "gray.400" : undefined}>Failover Model</Text>
                        <Tooltip content="Backup model used if the primary model fails or is unavailable.">
                          <Box cursor="help">
                            <LuInfo size={14} opacity={0.6} />
                          </Box>
                        </Tooltip>
                      </HStack>
                      <Combobox.Root
                        collection={modelCollection}
                        value={[formData.failover_model || '']}
                        onValueChange={(e) => updateField('failover_model', e.value[0] || '')}
                        openOnClick
                      >
                        <Combobox.Control position="relative">
                          <Combobox.Input
                            placeholder="Select failover model"
                            paddingRight="2rem"
                          />
                          <Combobox.Trigger position="absolute" right="0.5rem" top="50%" transform="translateY(-50%)">
                            <FaChevronDown size={16} />
                          </Combobox.Trigger>
                        </Combobox.Control>
                        <Combobox.Positioner>
                          <Combobox.Content>
                            {modelOptions.map(option => (
                              <Combobox.Item key={option.value} item={option.value}>
                                <Combobox.ItemText>{option.label}</Combobox.ItemText>
                                <Combobox.ItemIndicator />
                              </Combobox.Item>
                            ))}
                          </Combobox.Content>
                        </Combobox.Positioner>
                      </Combobox.Root>
                    </Box>
                  </HStack>
                </VStack>
              </Box>

              {/* Parameters */}
              <Box opacity={!formData.repo ? 0.5 : 1}>
                <Text fontSize="lg" fontWeight="semibold" mb={4}>
                  Parameters
                </Text>
                <VStack gap={4} align="stretch">
                  <HStack gap={4}>
                    <Box flex={1}>
                      <HStack mb={2}>
                        <Text fontWeight={formData.repo ? "medium" : "normal"} color={!formData.repo ? "gray.400" : undefined}>Temperature</Text>
                        <Tooltip content="Controls randomness. Higher values (up to 2) make output more creative, lower values more focused.">
                          <Box cursor="help">
                            <LuInfo size={14} opacity={0.6} />
                          </Box>
                        </Tooltip>
                      </HStack>
                      <NumberInput.Root
                        size="sm"
                        inputMode="decimal"
                        onValueChange={(e) => handleTemperatureChange(e.value)}
                        min={0}
                        max={2}
                        step={0.01}
                        value={formData.temperature?.toString() || '0.0'}
                      >
                        <NumberInput.Input />
                        <NumberInput.Control />
                      </NumberInput.Root>
                    </Box>

                    <Box flex={1}>
                      <HStack mb={2}>
                        <Text fontWeight={formData.repo ? "medium" : "normal"} color={!formData.repo ? "gray.400" : undefined}>Top P (0.00 - 1.00)</Text>
                        <Tooltip content="Probability mass for nucleus sampling. Lower values restrict possible outputs, higher values allow more diversity.">
                          <Box cursor="help">
                            <LuInfo size={14} opacity={0.6} />
                          </Box>
                        </Tooltip>
                      </HStack>
                      <NumberInput.Root
                        size="sm"
                        inputMode="decimal"
                        onValueChange={(e) => handleTopPChange(e.value)}
                        min={0}
                        max={1}
                        step={0.01}
                        value={formData.top_p?.toString() || '1.0'}
                      >
                        <NumberInput.Input />
                        <NumberInput.Control />
                      </NumberInput.Root>
                    </Box>

                    <Box flex={1}>
                      <HStack mb={2}>
                        <Text fontWeight={formData.repo ? "medium" : "normal"} color={!formData.repo ? "gray.400" : undefined}>Max Tokens</Text>
                        <Tooltip content="Maximum number of tokens the model can generate in the response.">
                          <Box cursor="help">
                            <LuInfo size={14} opacity={0.6} />
                          </Box>
                        </Tooltip>
                      </HStack>
                      <NumberInput.Root
                        size="sm"
                        inputMode="decimal"
                        onValueChange={(e) => updateField('max_tokens', parseInt(e.value) || 2048)}
                        min={1}
                        max={100000}
                        step={1}
                        value={formData.max_tokens?.toString() || '2048'}
                      >
                        <NumberInput.Input />
                        <NumberInput.Control />
                      </NumberInput.Root>
                    </Box>
                  </HStack>

                  <VStack gap={4} align="stretch">
                    <HStack justify="space-between" align="center">
                      <VStack align="start" gap={1}>
                        <HStack>
                          <Text fontWeight={formData.repo ? "medium" : "normal"} color={!formData.repo ? "gray.400" : undefined}>Enable Thinking</Text>
                          <Tooltip content="Allows the model to reason step by step for more complex tasks.">
                            <Box cursor="help">
                              <LuInfo size={14} opacity={0.6} />
                            </Box>
                          </Tooltip>
                        </HStack>
                        <Text fontSize="sm" color={!formData.repo ? "gray.400" : mutedTextColor}>
                          Allow the model to think through problems step by step
                        </Text>
                      </VStack>
                      <Switch.Root
                        checked={formData.thinking_enabled || false}
                        onCheckedChange={(e: { checked: boolean }) => updateField('thinking_enabled', e.checked)}
                        size="lg"
                      >
                        <Switch.HiddenInput />
                        <Switch.Control>
                          <Switch.Thumb />
                        </Switch.Control>
                        <Switch.Label />
                      </Switch.Root>
                    </HStack>

                    {formData.thinking_enabled && (
                      <Box>
                        <HStack mb={2}>
                          <Text fontWeight={formData.repo ? "medium" : "normal"} color={!formData.repo ? "gray.400" : undefined}>Thinking Budget</Text>
                          <Tooltip content="Limits the number of tokens the model can use for step-by-step reasoning.">
                            <Box cursor="help">
                              <LuInfo size={14} opacity={0.6} />
                            </Box>
                          </Tooltip>
                        </HStack>
                        <NumberInput.Root
                          size="sm"
                          inputMode="decimal"
                          onValueChange={(e) => updateField('thinking_budget', parseInt(e.value) || 20000)}
                          min={1000}
                          max={100000}
                          step={1000}
                          value={formData.thinking_budget?.toString() || '20000'}
                        >
                          <NumberInput.Input />
                          <NumberInput.Control />
                        </NumberInput.Root>
                      </Box>
                    )}
                  </VStack>
                </VStack>
              </Box>
            </VStack>
        </Box>
      </VStack>
    </Box>
  );
}