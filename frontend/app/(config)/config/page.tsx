"use client"

import { Box, Container, VStack } from '@chakra-ui/react'
import { useRouter } from 'next/navigation'
import LLMStep from '../_components/LLMConfigStep'
import ReposConfigStep from '../_components/ReposConfigStep'
import { useConfigState } from '../_state/configState'
import { ConfigHeader } from '../_components/ConfigHeader'
import { ConfigService } from '@/services/config/configService'
import { LoadingOverlay } from '@/components/LoadingOverlay'

export default function ConfigPage() {
  const router = useRouter()
  
  const {
    configState,
    updateCurrentStepField,
    addLLMConfig: addLLMConfigAction,
    removeLLMConfig: removeLLMConfigAction,
    setIsSaving,
    addRepoConfig,
    removeRepoConfig,
  } = useConfigState();

  const handleSave = async () => {
    setIsSaving(true);
    try {
      // Save the complete configuration including both LLM and repo configs
      await ConfigService.updateConfig({
        ...configState.config,
        llm_configs: configState.config.llm_configs,
        repo_configs: configState.repos.configured
      });
      router.push('/');
    } finally {
      setIsSaving(false);
    }
  };

  // Show loading screen while initial data is being fetched
  if (configState.isLoading) {
    return (
      <Box
        minH="100vh"
        display="flex"
        alignItems="center"
        justifyContent="center"
      >
        <LoadingOverlay
          isVisible={true}
          title="Loading Configuration..."
          subtitle="Please wait while we load your settings"
        />
      </Box>
    );
  }

  // Show loading screen while saving configurations
  if (configState.isSaving) {
    return (
      <Box
        minH="100vh"
        display="flex"
        alignItems="center"
        justifyContent="center"
      >
        <LoadingOverlay
          isVisible={true}
          title="Saving Configuration..."
          subtitle="Please wait while we save your settings"
        />
      </Box>
    );
  }

  return (
    <Box width="100%">
      <VStack gap={8} align="stretch">
        <ConfigHeader
          onSave={handleSave}
          isLoading={configState.isSaving}
        />
        <Container maxW="7xl" py={6}>
          {/* LLM Provider Configuration */}
          <Box mb={6}>
            <LLMStep
              selectedProvider={configState.currentStep.selectedProvider || ''}
              setSelectedProvider={(provider: string) => updateCurrentStepField('selectedProvider', provider)}
              selectedModel={configState.currentStep.selectedModel || ''}
              setSelectedModel={(model: string) => updateCurrentStepField('selectedModel', model)}
              apiKey={configState.currentStep.apiKey || ''}
              setApiKey={(key: string) => updateCurrentStepField('apiKey', key)}
              apiBaseUrl={configState.currentStep.apiBaseUrl || ''}
              setApiBaseUrl={(url: string) => updateCurrentStepField('apiBaseUrl', url)}
              llmConfigs={configState.config.llm_configs || []}
              addLLMConfig={addLLMConfigAction}
              removeLLMConfig={removeLLMConfigAction}
              disabled={configState.isSaving}
              availableProviders={configState.providers.available || []}
              isLoadingProviders={configState.providers.isLoading}
            />
          </Box>
          
          {/* Repository Configuration */}
          <Box mb={6}>
            <ReposConfigStep
              hostingType={configState.config.hosting_config.type}
              disabled={configState.isSaving}
              repos={configState.repos.available}
              configuredRepos={configState.repos.configured}
              isLoadingRepos={configState.repos.isLoading}
              isLoadingConfiguredRepos={configState.repos.isLoading}
              addRepoConfig={addRepoConfig}
              removeRepoConfig={removeRepoConfig}
            />
          </Box>
        </Container>
      </VStack>
    </Box>
  )
}