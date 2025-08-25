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
  Card,
  Container,
  Switch,
} from '@chakra-ui/react';
import { Tooltip } from '@/components/ui/tooltip';
import { FaChevronDown } from 'react-icons/fa';
import { LuArrowLeft, LuInfo } from 'react-icons/lu';
import { useColorModeValue } from '@/components/ui/color-mode';
import { Prompt } from '../_state/promptState';
import { getModelOptions } from '../_lib/mockData';

interface PromptEditorProps {
  prompt: Prompt | null;
  onSave: (updates: Partial<Prompt>) => void;
  onBack: () => void;
}

export function PromptEditor({ prompt, onSave, onBack }: PromptEditorProps) {
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

  // Theme colors
  const cardBg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
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
    }
  }, [prompt]);

  const updateField = (field: keyof Prompt, value: string | number | boolean) => {
    const updatedData = { ...formData, [field]: value };
    setFormData(updatedData);
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

  if (!prompt) {
    return (
      <Container maxW="6xl" py={6}>
        <Text>Loading...</Text>
      </Container>
    );
  }

  return (
    <Container maxW="6xl" py={6}>
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
                {prompt.name || 'New Prompt'}
              </Text>
              <Text fontSize="sm" color={mutedTextColor}>
                Edit prompt settings and configuration. Changes are saved automatically.
              </Text>
            </VStack>
          </HStack>
        </HStack>

        {/* Form */}
        <Card.Root bg={cardBg} borderColor={borderColor}>
          <Card.Body p={6}>
            <VStack gap={6} align="stretch">
              {/* Basic Info */}
              <Box>
                <Text fontSize="lg" fontWeight="semibold" mb={4}>
                  Basic Information
                </Text>
                <VStack gap={4} align="stretch">
                  <Box>
                    <Text mb={2} fontWeight="medium">Name</Text>
                    <Input
                      value={formData.name || ''}
                      onChange={(e) => updateField('name', e.target.value)}
                      placeholder="Enter prompt name"
                    />
                  </Box>

                  <Box>
                    <Text mb={2} fontWeight="medium">Description</Text>
                    <Textarea
                      value={formData.description || ''}
                      onChange={(e) => updateField('description', e.target.value)}
                      placeholder="Describe what this prompt does"
                      rows={3}
                    />
                  </Box>

                  <Box>
                    <Text mb={2} fontWeight="medium" fontSize="lg">Prompt Template</Text>
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
              <Box>
                <Text fontSize="lg" fontWeight="semibold" mb={4}>
                  Model Configuration
                </Text>
                <VStack gap={4} align="stretch">
                  <HStack gap={4}>
                    <Box flex={1}>
                      <HStack mb={2}>
                        <Text fontWeight="medium">Primary Model</Text>
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
                        <Text fontWeight="medium">Failover Model</Text>
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
              <Box>
                <Text fontSize="lg" fontWeight="semibold" mb={4}>
                  Parameters
                </Text>
                <VStack gap={4} align="stretch">
                  <HStack gap={4}>
                    <Box flex={1}>
                      <HStack mb={2}>
                        <Text fontWeight="medium">Temperature</Text>
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
                        <Text fontWeight="medium">Top P (0.00 - 1.00)</Text>
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
                        <Text fontWeight="medium">Max Tokens</Text>
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
                          <Text fontWeight="medium">Enable Thinking</Text>
                          <Tooltip content="Allows the model to reason step by step for more complex tasks.">
                            <Box cursor="help">
                              <LuInfo size={14} opacity={0.6} />
                            </Box>
                          </Tooltip>
                        </HStack>
                        <Text fontSize="sm" color={mutedTextColor}>
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
                          <Text fontWeight="medium">Thinking Budget</Text>
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
          </Card.Body>
        </Card.Root>
      </VStack>
    </Container>
  );
}