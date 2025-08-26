'use client';

import React from 'react';
import {
  Box,
  VStack,
  createListCollection,
} from '@chakra-ui/react';
import { Prompt } from '@/types/Prompt';
import { getModelOptions } from '../_lib/getConfiguredModels';
import { Repo } from '@/types/Repo';
import { PromptEditorHeader } from './PromptEditorHeader';
import { PromptFieldGroup } from './PromptFieldGroup';
import { ModelFieldGroup } from './ModelFieldGroup';
import { ParametersFieldGroup } from './ParametersFieldGroup';
import { EnableThinkingFieldGroup } from './EnableThinkingFieldGroup';

interface PromptEditorProps {
  prompt: Prompt | null;
  onSave: (updates: Partial<Prompt>) => void;
  onBack: () => void;
  configuredRepos?: Array<Repo>;
  isSaving?: boolean;
}

export function PromptEditor({ prompt, onSave, onBack, configuredRepos = [], isSaving = false }: PromptEditorProps) {
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


  const modelOptions = getModelOptions();
  const modelCollection = createListCollection({
    items: modelOptions
  });

  // Initialize and update form data when prompt changes
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
        repo: undefined,
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
  };

  const updateRepoField = (repo: Repo | undefined) => {
    const updatedData = { ...formData, repo };
    setFormData(updatedData);
    setShowRepoError(false); // Clear error when repository is selected
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

  const handleSave = () => {
    if (!formData.repo) {
      setShowRepoError(true);
      return;
    }
    onSave(formData);
  };

  return (
    <Box p={6} borderWidth="1px" borderRadius="md" borderColor="border.emphasized">
      <VStack gap={6} align="stretch">
        {/* Header */}
        <PromptEditorHeader
          displayPrompt={displayPrompt}
          onBack={onBack}
          onSave={handleSave}
          canSave={!!formData.repo}
          isSaving={isSaving}
        />

        {/* Form */}
        <Box p={6} borderWidth="1px" borderRadius="md" borderColor="border.muted">
          <VStack gap={6} align="stretch">
            {/* Basic Info */}
            <PromptFieldGroup
              formData={formData}
              configuredRepos={configuredRepos}
              showRepoError={showRepoError}
              updateField={updateField}
              updateRepoField={updateRepoField}
            />

            {/* Model Configuration */}
            <ModelFieldGroup
              formData={formData}
              modelCollection={modelCollection}
              updateField={updateField}
            />

            {/* Parameters */}
            <ParametersFieldGroup
              formData={formData}
              updateField={updateField}
              handleTemperatureChange={handleTemperatureChange}
              handleTopPChange={handleTopPChange}
            />

            {/* Thinking Configuration */}
            <Box opacity={!formData.repo ? 0.5 : 1}>
              <EnableThinkingFieldGroup
                formData={formData}
                updateField={updateField}
              />
            </Box>

          </VStack>
        </Box>
      </VStack>
    </Box>
  );
}