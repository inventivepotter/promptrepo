'use client';

import React from 'react';
import {
  Box,
  VStack,
  HStack,
} from '@chakra-ui/react';
import { useColorModeValue } from '@/components/ui/color-mode';
import { Prompt } from '@/types/Prompt';
import { Repo } from '@/types/Repo';
import { PromptEditorHeader } from './PromptEditorHeader';
import { PromptFieldGroup } from './PromptFieldGroup';
import { ModelFieldGroup } from './ModelFieldGroup';
import { ParametersFieldGroup } from './ParametersFieldGroup';
import { EnableThinkingFieldGroup } from './EnableThinkingFieldGroup';
import { Chat } from './Chat';
import { PromptTimeline } from './PromptTimeline';
import { LLMProvider } from '@/types/LLMProvider';
import { promptsService } from '@/services/prompts';
import { useAuth } from '../../(auth)/_components/AuthProvider';


interface PromptEditorProps {
  prompt: Prompt | null;
  onSave: (updates: Partial<Prompt>) => void;
  onBack: () => void;
  configuredRepos?: Array<Repo>;
  configuredModels?: Array<LLMProvider>;
  isSaving?: boolean;
}

export function PromptEditor({ prompt, onSave, onBack, configuredRepos = [], configuredModels = [], isSaving = false }: PromptEditorProps) {
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
  const [originalData, setOriginalData] = React.useState<Partial<Prompt>>({});
  const [hasUnsavedChanges, setHasUnsavedChanges] = React.useState(false);
  const [changesSaved, setChangesSaved] = React.useState(false);
  const [showRepoError, setShowRepoError] = React.useState(false);
  const [isCommitPushing, setIsCommitPushing] = React.useState(false);

  
  

  // Initialize and update form data when prompt changes
  React.useEffect(() => {
    const initialData = prompt ? {
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
    } : {
      // Initialize with default values for new prompts
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
    };

    setFormData(initialData);
    setOriginalData(initialData);
    setHasUnsavedChanges(false);
    setChangesSaved(false);
  }, [prompt]);

  // Check if form data has changed from original
  React.useEffect(() => {
    const hasChanges = JSON.stringify(formData) !== JSON.stringify(originalData);
    setHasUnsavedChanges(hasChanges);
    if (hasChanges) {
      setChangesSaved(false);
    }
  }, [formData, originalData]);

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
    setChangesSaved(true);
    setOriginalData(formData);
    setHasUnsavedChanges(false);
  };

  const handleChatMessage = (message: string, tools: string[]) => {
    // Here you would typically send the message to your AI agent
    // along with the current prompt configuration and selected tools
    console.log('Chat message:', { message, tools, promptConfig: formData });
  };

  const handleCommitPush = async () => {
    if (!prompt?.id) {
      console.error('No prompt ID available for commit & push');
      return;
    }
    
    setIsCommitPushing(true);
    try {
      await promptsService.commitPushPrompt(prompt.id);
    } finally {
      setIsCommitPushing(false);
    }
  };

  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const bgColor = useColorModeValue('gray.50', 'gray.900');

  const { user } = useAuth();

  // Get commits from prompt data with 0th commit for latest changes
  const commits = React.useMemo(() => {
    const draftCommit = {
      id: '0',
      message: '',
      author: user?.name || user?.username || 'Unknown User',
      date: new Date().toISOString(),
      hash: 'draft',
      isLatest: true
    };

    if (prompt?.recent_commits && prompt.recent_commits.length > 0) {
      // Add the draft commit at position 0, then the API commits
      return [
        draftCommit,
        ...prompt.recent_commits.map((commit) => ({
          ...commit,
          id: commit.hash,
          isLatest: false
        }))
      ];
    }
    
    // Return just the draft commit if no API commits available
    return [draftCommit];
  }, [prompt?.recent_commits, user?.name, user?.username]);

  return (
    <Box>
      {/* Sticky Header */}
      <Box
        position="sticky"
        top={0}
        zIndex={10}
        bg={bgColor}
        borderBottomWidth="1px"
        borderColor={borderColor}
        p={6}
        pb={4}
      >
        <PromptEditorHeader
          displayPrompt={displayPrompt}
          onBack={onBack}
          onSave={handleSave}
          canSave={!!formData.repo && hasUnsavedChanges}
          isSaving={isSaving}
          onCommitPush={handleCommitPush}
          isCommitPushing={isCommitPushing}
          canCommitPush={!!formData.repo && !hasUnsavedChanges}
        />
      </Box>

      {/* Main Content - Three column layout with timeline */}
      <Box p={6} pt={2}>
        <HStack gap={6} align="start" minH="600px">
          {/* Left Section - Form */}
          <Box
            p={6}
            borderWidth="1px"
            borderRadius="md"
            borderColor="border.muted"
            width="54%"
          >
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
                configuredModels={configuredModels}
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

          {/* Middle Section - Timeline (1%) */}
          <Box
            width="1%"
            minW="20px"
            height="200vh"
            pt={4}
          >
            <PromptTimeline commits={commits} />
          </Box>

          {/* Right Section - Chat (remaining space) */}
          <Box
            width="45%"
          >
            <Chat
              height="700px"
              onMessageSend={handleChatMessage}
              promptData={{
                prompt: formData.prompt || '',
                model: formData.model || '',
                temperature: formData.temperature || 0.7,
                max_tokens: formData.max_tokens || 2048,
                top_p: formData.top_p || 1.0,
              }}
            />
          </Box>
        </HStack>
      </Box>
    </Box>
  );
}