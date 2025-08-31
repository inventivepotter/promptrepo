"use client"

import { Box, Container, VStack } from '@chakra-ui/react'
import HostingStep from '../_components/HostingStep'
import AuthStep from '../_components/AuthStep'
import LLMStep from '../_components/LLMStep'
import AdminConfigStep from '../_components/AdminConfigStep'
import Configurations from '../_components/DownloadConfigurations'
import { useConfigState } from '../_state/configState'
import { ConfigHeader } from '../_components/ConfigHeader'
import { postConfig } from '../_lib/postConfig'
import { LoadingOverlay } from '@/components/LoadingOverlay'
import { UnauthorizedScreen } from '@/components/UnauthorizedScreen'

export default function ConfigPage() {
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
      await postConfig(configState.config);
    } finally {
      setIsLoading(false);
    }
  };

  // Show unauthorized screen if loading or any error exists
  if (configState.isLoading || configState.error) {
    return (
      <UnauthorizedScreen />
    );
  }

  return (
    <Box width="100%">
      <LoadingOverlay
        isVisible={configState.isLoading}
        title="Saving Configuration..."
        subtitle="Please wait while we save your settings"
      />
      <VStack gap={8} align="stretch">
        <ConfigHeader onSave={handleSave} isLoading={configState.isLoading} />
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
              apiBaseUrl={configState.currentStep.apiBaseUrl}
              setApiBaseUrl={(url: string) => updateCurrentStepField('apiBaseUrl', url)}
              llmConfigs={configState.config.llmConfigs}
              addLLMConfig={addLLMConfigAction}
              removeLLMConfig={removeLLMConfigAction}
              disabled={configState.isLoading}
              availableProviders={configState.providers.available}
              isLoadingProviders={configState.providers.isLoading}
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
                  if (config.apiBaseUrl) {
                    envContent += `${providerKey}_API_BASE_URL=${config.apiBaseUrl}\n`
                  }
                })
                if (configState.config.adminEmails.length > 0) {
                  envContent += '\n# Admin Configuration\n'
                  envContent += `ADMIN_EMAILS=${configState.config.adminEmails.join(',')}\n`
                }
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
            <AdminConfigStep
              adminEmails={configState.config.adminEmails}
              setAdminEmails={(emails) => updateConfigField("adminEmails", emails)}
              disabled={configState.isLoading}
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