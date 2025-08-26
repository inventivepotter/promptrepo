"use client"

import { Box, Container, VStack } from '@chakra-ui/react'
import HostingStep from '../_components/HostingStep'
import AuthStep from '../_components/AuthStep'
import LLMStep from '../_components/LLMStep'
import Configurations from '../_components/DownloadConfigurations'
import { useConfigState } from '../_state/configState'
import { SetupHeader } from '../_components/SetupHeader'
import { postConfigData } from '../_lib/postConfigData'
import { LoadingOverlay } from '@/components/LoadingOverlay'

export default function SetupPage() {
  const {
    configState,
    setConfigState: updateConfigState,
    updateConfigField,
    updateCurrentStepField,
    addLLMConfig: addLLMConfigAction,
    removeLLMConfig: removeLLMConfigAction,
    setIsLoading,
  } = useConfigState();

  const handleSave = async () => {
    setIsLoading(true);
    try {
      await postConfigData(configState.config);
    } catch (error) {
      console.error('Failed to persist config to backend:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Box width="100%">
      <LoadingOverlay
        isVisible={configState.isLoading}
        title="Saving Configuration..."
        subtitle="Please wait while we save your settings"
      />
      <VStack gap={8} align="stretch">
        <SetupHeader onSave={handleSave} isLoading={configState.isLoading} />
        <Container maxW="7xl" py={6}>
          <Box mb={6}>
            <HostingStep
              hostingType={configState.config.hostingType}
              setHostingType={(type) => updateConfigField("hostingType", type)}
              disabled={configState.isLoading}
            />
          </Box>
          <Box mb={6}>
            <AuthStep
              hostingType={configState.config.hostingType}
              githubClientId={configState.config.githubClientId}
              githubClientSecret={configState.config.githubClientSecret}
              setGithubClientId={(id) => updateConfigField("githubClientId", id)}
              setGithubClientSecret={(secret) => updateConfigField("githubClientSecret", secret)}
              disabled={configState.isLoading}
            />
          </Box>
          <Box mb={6}>
            <LLMStep
              selectedProvider={configState.currentStep.selectedProvider}
              setSelectedProvider={(provider: string) => updateCurrentStepField('selectedProvider', provider)}
              selectedModel={configState.currentStep.selectedModel}
              setSelectedModel={(model: string) => updateCurrentStepField('selectedModel', model)}
              apiKey={configState.currentStep.apiKey}
              setApiKey={(key: string) => updateCurrentStepField('apiKey', key)}
              llmConfigs={configState.config.llmConfigs}
              addLLMConfig={addLLMConfigAction}
              removeLLMConfig={removeLLMConfigAction}
              disabled={configState.isLoading}
              downloadEnvFile={() => {
                let envContent = '# Generated Environment Configuration\n\n'
                envContent += `HOSTING_TYPE=${configState.config.hostingType}\n\n`
                if (configState.config.hostingType === 'multi-user') {
                  envContent += '# GitHub OAuth Configuration\n'
                  envContent += `GITHUB_CLIENT_ID=${configState.config.githubClientId}\n`
                  envContent += `GITHUB_CLIENT_SECRET=${configState.config.githubClientSecret}\n\n`
                }
                envContent += '# LLM Provider Configurations\n'
                configState.config.llmConfigs.forEach((config) => {
                  const providerKey = config.provider.toUpperCase()
                  envContent += `${providerKey}_API_KEY=${config.apiKey}\n`
                  envContent += `${providerKey}_MODEL=${config.model}\n`
                })
                const blob = new Blob([envContent], { type: 'text/plain' })
                const url = URL.createObjectURL(blob)
                const a = document.createElement('a')
                a.href = url
                a.download = '.env'
                document.body.appendChild(a)
                a.click()
                document.body.removeChild(a)
                URL.revokeObjectURL(url)
              }}
            />
          </Box>
          <Box mb={6}>
            <Configurations downloadEnvFile={() => {}} />
          </Box>
        </Container>
      </VStack>
    </Box>
  )
}